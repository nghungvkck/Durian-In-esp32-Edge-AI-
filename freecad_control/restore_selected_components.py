from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part,zipfile,shutil,json,hashlib
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
source_path=path.parent/'Shells_Only/D36_before_removing_components.FCStd'
out=path.parent/'Selected_Components';out.mkdir(exist_ok=True)
backup=out/'D36_before_restoring_components.FCStd'
assert not backup.exists(), 'Already attempted; inspect before rerun'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
keep=('Front_half','Rear_half','Screw_M3_1','Screw_M3_2','Nut_M3_1','Nut_M3_2')
assert set(o.Name for o in doc.Objects)==set(keep)
names=['Battery','MicroSD','IP5306','ESP32_C3','SW1','SW1_Terminals','Key_PCB','Key_Mount_Rings','Key_Pads']
names += [f'Key_{part}_{i}' for i in (1,2,3) for part in ('Case','Body','Stem','Leads')]
names += ['Mic_PCB','Mic_ICS43434','Mic_Pads','Mic_Passives']
shutil.copy2(path,backup)
source=App.openDocument(str(source_path))
try:
    for name in names:
        original=source.getObject(name);assert original is not None,name
        obj=doc.copyObject(original,False)
        assert obj.Name==name
        assert str(obj.Placement)==str(original.Placement)
        assert abs(obj.Shape.Volume-original.Shape.Volume)<1e-7
        obj.Visibility=True
    doc.Battery.Label='Pin 35 x 25 x 6 mm'
finally:
    App.closeDocument(source.Name)
App.setActiveDocument(doc.Name)
for obj in doc.Objects: obj.Visibility=True
doc.recompute();Gui.Selection.clearSelection();doc.save()
def compare_payload(a,b,name):
    if a==b:return
    x=a.split();y=b.split();assert len(x)==len(y),name+' token count'
    for i,j in zip(x,y):
        if i==j:continue
        if (i,j) in ((b'0101000',b'0111000'),(b'0111000',b'0101000')):continue
        assert abs(float(i)-float(j))<1e-12,name+' geometry token'
with zipfile.ZipFile(source_path) as source_zip,zipfile.ZipFile(backup) as old,zipfile.ZipFile(path) as new:
    newxml=ET.fromstring(new.read('Document.xml'))
    for archive,selected in ((source_zip,names),(old,keep)):
        xml=ET.fromstring(archive.read('Document.xml'))
        for name in selected:
            a=xml.find("./ObjectData/Object[@name='%s']"%name)
            b=newxml.find("./ObjectData/Object[@name='%s']"%name)
            p="./Properties/Property[@name='Shape']/Part"
            compare_payload(archive.read(a.find(p).attrib['file']),new.read(b.find(p).attrib['file']),name)
            p="./Properties/Property[@name='Placement']/PropertyPlacement"
            assert a.find(p).attrib==b.find(p).attrib,name+' placement'
    for name in keep:
        node=newxml.find("./ObjectData/Object[@name='%s']"%name)
        data=new.read(node.find("./Properties/Property[@name='Shape']/Part").attrib['file'])
        tmp=out/'verify.brp';tmp.write_bytes(data)
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1,name
assert len(doc.Objects)==31
report={'restored':names,'restored_count':len(names),'object_count':len(doc.Objects),'shells_and_fasteners_unchanged':True,'restored_geometry_and_placements_match_source':True,'view':'Closed assembled shell, components visible at installed coordinates; shell opaque. No TPU, standalone R/C, LED, gasket or preview objects.','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup)}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
