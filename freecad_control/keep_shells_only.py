from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part, shutil,zipfile,hashlib,json
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Shells_Only'; out.mkdir(exist_ok=True)
backup=out/'D36_before_removing_components.FCStd'
assert not backup.exists(), 'Backup exists; inspect before retry'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
keep=('Front_half','Rear_half','Screw_M3_1','Screw_M3_2','Nut_M3_1','Nut_M3_2')
assert all(doc.getObject(n) for n in keep)
shutil.copy2(path,backup)
removed=[o.Name for o in doc.Objects if o.Name not in keep]
# Remove links first, then their source references.
for name in sorted(removed,key=lambda n:not n.startswith('Preview_')):
    doc.removeObject(name)
doc.recompute()
assert set(o.Name for o in doc.Objects)==set(keep)
for obj in doc.Objects:
    obj.Visibility=True
    assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
doc.save()
checked={}
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml')); newxml=ET.fromstring(after.read('Document.xml'))
    for name in keep:
        old=oldxml.find("./ObjectData/Object[@name='%s']"%name)
        new=newxml.find("./ObjectData/Object[@name='%s']"%name)
        p="./Properties/Property[@name='Shape']/Part"
        data=after.read(new.find(p).attrib['file'])
        assert before.read(old.find(p).attrib['file'])==data,name+' geometry changed'
        p="./Properties/Property[@name='Placement']/PropertyPlacement"
        assert old.find(p).attrib==new.find(p).attrib,name+' moved'
        tmp=out/'verify.brp'; tmp.write_bytes(data)
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume}
Gui.Selection.clearSelection()
report={'kept':list(keep),'removed':removed,'object_count':len(doc.Objects),'geometry_and_placement_of_kept_objects_unchanged':True,'saved_BRep':checked,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup)}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
