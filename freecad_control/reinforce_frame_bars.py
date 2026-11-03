"""Thicken existing rear frame and spread existing holder feet to sidewalls."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part,json,zipfile,hashlib,shutil
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Reinforced_Frame';out.mkdir(exist_ok=True)
backup=out/'D36_before_reinforcing_frame.FCStd'
assert not backup.exists(),'Already attempted; inspect before rerun'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
assert len(doc.Objects)==33
assert abs(doc.Front_half.Shape.Volume-29107.368581411152)<.001
assert abs(doc.Rear_half.Shape.Volume-29796.112525501958)<.001
shutil.copy2(path,backup)
V=App.Vector
anchor=Part.makeCylinder(16.8,146)
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
features=[]
def add(label,half,bounds):
    s=box(*bounds).common(anchor)
    assert s.isValid() and s.Volume>.01,label
    features.append((label,half,s,bounds))
# Preserve battery-facing planes. Thicken away from the battery and into walls.
for z0,z1 in ((32,36),(54,58)):
    add('Battery_crossbar_'+str(z0),'Rear_half',(-13.6,13.6,-6.224074074,-4.624074074,z0-.6,z1+.6))
    for side,x0,x1 in (('left',-16.8,-13.3),('right',13.3,16.8)):
        add('Battery_crossbar_foot_'+str(z0)+'_'+side,'Rear_half',(x0,x1,-16.8,0,z0-.6,z1+.6))
for label,z0,z1 in (('lower',24.1,25.7),('upper',62.3,63.9)):
    add('Battery_end_'+label,'Rear_half',(-16.8,16.8,-6.224074074,0,z0,z1))
    for side,x0,x1 in (('left',-16.8,-13.3),('right',13.3,16.8)):
        add('Battery_end_foot_'+label+'_'+side,'Rear_half',(x0,x1,-16.8,0,z0,z1))
# Front: broaden existing SD, ESP and button-board feet outward; keep PCB-facing edges.
add('SD_left_foot','Front_half',(-16.8,-12.25,4.425925926,16.8,23.25,29.4))
add('SD_right_foot','Front_half',(12.25,16.8,4.425925926,16.8,61.6,67.75))
add('Keys_left_foot','Front_half',(-16.8,-7.75,9.95,16.8,73.25,79.4))
add('Keys_right_foot','Front_half',(7.75,16.8,9.95,16.8,105.6,111.75))
# Behind ESP's rear face; Y>=5.45 also preserves the side USB cutout (Y<=5.2).
add('ESP_left_foot','Front_half',(-16.8,-8.75,5.45,16.8,87.1,89.1))
add('ESP_right_foot','Front_half',(14.45,16.8,5.45,16.8,76.35,78.35))
# Rear IP feet remain behind the PCB, and mic receives a wider base under its one-end U.
add('IP_left_foot','Rear_half',(-16.8,-13.85,-16.8,-5.25,72.25,78.4))
add('IP_right_foot','Rear_half',(9.85,16.8,-16.8,-5.25,89.6,95.75))
add('Mic_bottom_base','Rear_half',(-16.8,16.8,-16.8,-14.05,96.27,100))
shells={n:doc.getObject(n).Shape.copy() for n in ('Front_half','Rear_half')}
others=[o for o in doc.Objects if o.Name not in shells]
records=[]
for label,half,shape,bounds in features:
    addition=shape.cut(shells[half])
    checks=[]
    for obj in others:
        a=addition.BoundBox;b=obj.Shape.optimalBoundingBox(False,False)
        gaps=[max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max')) for k in ('X','Y','Z')]
        if max(gaps)>.19:
            continue
        distance=addition.distToShape(obj.Shape)[0]
        volume=addition.common(obj.Shape).Volume
        assert volume<1e-6 and distance>.19,(label,obj.Name,volume,distance)
        checks.append({'component':obj.Name,'distance_mm':distance})
    shells[half]=shells[half].fuse(shape)
    records.append({'name':label,'half':half,'box_before_cylinder_clip':list(bounds),'added_volume_mm3':addition.Volume,'near_checks':checks})
for name,s in shells.items():
    assert s.isValid() and len(s.Solids)==1,name
    b=s.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<.001 and abs(b.ZLength-146)<.001
assert shells['Front_half'].common(shells['Rear_half']).Volume<1e-6
for name,s in shells.items():doc.getObject(name).Shape=s;doc.getObject(name).ViewObject.DisplayMode='Shaded'
doc.recompute();Gui.Selection.clearSelection();doc.save()
checked={}
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml'));newxml=ET.fromstring(after.read('Document.xml'))
    for obj in others:
        name=obj.Name;a=oldxml.find("./ObjectData/Object[@name='%s']"%name);b=newxml.find("./ObjectData/Object[@name='%s']"%name)
        p="./Properties/Property[@name='Shape']/Part"
        aa=before.read(a.find(p).attrib['file']).split();bb=after.read(b.find(p).attrib['file']).split()
        assert len(aa)==len(bb),name
        for i,j in zip(aa,bb):
            if i==j or (i,j) in ((b'0101000',b'0111000'),(b'0111000',b'0101000')):continue
            assert abs(float(i)-float(j))<1e-12,name+' geometry'
        p="./Properties/Property[@name='Placement']/PropertyPlacement"
        assert a.find(p).attrib==b.find(p).attrib,name+' placement'
    for name in shells:
        node=newxml.find("./ObjectData/Object[@name='%s']"%name)
        tmp=out/'verify.brp';tmp.write_bytes(after.read(node.find("./Properties/Property[@name='Shape']/Part").attrib['file']))
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-shells[name].Volume)<1e-6
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume}
report={'change':'Reinforce existing guides in both shells; no new mirrored battery frame in front. Rear crossbar backing 0.8->1.6 mm, width4->5.2; end bars 0.8->1.6. Feet spread toward both sidewalls. Front SD/keys/ESP feet and rear IP/mic base broadened outward.','features':records,'saved_BRep':checked,'unchanged_component_and_hardware_objects':len(others),'dimensions_mm':[36,146],'objects':len(doc.Objects),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitations':'Static clearances only; physical retention, insertion, printability and strength untested. Existing PCB/battery-facing contact planes retained. No TPU or old pockets restored.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
