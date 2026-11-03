from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part,json,zipfile,hashlib,shutil
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Simplified_Holder_Steps';out.mkdir(exist_ok=True)
backup=out/'D36_before_simplifying_holder_steps.FCStd'
assert not backup.exists(),'Already attempted; inspect before rerun'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
assert len(doc.Objects)==31
shutil.copy2(path,backup)
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))
specs=[
 ('SD_A','Front_half',(-11.9,-10.8),5.675925926,1,(16,18.5)),
 ('SD_B','Front_half',(10.8,11.9),5.675925926,1,(52,54.5)),
 ('IP_A','Rear_half',(-14.4,-13.3),-5,-1,(65,67.5)),
 ('IP_B','Rear_half',(9.3,10.4),-5,-1,(80,82.5)),
 ('ESP_A','Front_half',(-8.4,-7.3),5.1,1,(77.6,78.6)),
 ('ESP_B','Front_half',(13,14.1),5.1,1,(66.85,67.85)),
 ('Keys_A','Front_half',(-7.4,-6.3),11.8,1,(65,67.5)),
 ('Keys_B','Front_half',(6.3,7.4),11.8,1,(96,98.5))]
fills=[]
for label,half,(x0,x1),surface,direction,(z0,z1) in specs:
    a,b=sorted([surface,surface+direction*.8])
    fills.append((label,half,box(x0,x1,a,b,z0,z1)))
for z0,z1 in ((22,26),(44,48)):
    fills.append(('Battery_slot_'+str(z0),'Rear_half',box(-2,2,-5.424074074,-4.624074074,z0+.8,z1-.8)))
shapes={n:doc.getObject(n).Shape.copy() for n in ('Front_half','Rear_half')}
before_faces={n:len(s.Faces) for n,s in shapes.items()}
checks=[]
others=[o for o in doc.Objects if o.Name not in shapes]
for label,half,fill in fills:
    addition=fill.cut(shapes[half])
    assert addition.Volume>.01,label+' not a missing pocket'
    for obj in others:
        a=addition.BoundBox;b=obj.Shape.BoundBox
        if not all(getattr(a,k+'Max')>=getattr(b,k+'Min') and getattr(b,k+'Max')>=getattr(a,k+'Min') for k in ('X','Y','Z')):continue
        assert addition.common(obj.Shape).Volume<1e-6,label+' collides '+obj.Name
    shapes[half]=shapes[half].fuse(fill)
    checks.append({'feature':label,'half':half,'added_volume_mm3':addition.Volume})
refined={}
for name,s in shapes.items():
    assert s.isValid() and len(s.Solids)==1,name
    candidate=s.removeSplitter()
    accepted=candidate.isValid() and len(candidate.Solids)==1 and abs(candidate.Volume-s.Volume)<1e-6
    if accepted:s=candidate
    refined[name]=accepted
    b=s.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<.001 and abs(b.ZLength-136)<.001
    shapes[name]=s
assert shapes['Front_half'].common(shapes['Rear_half']).Volume<1e-6
for name,s in shapes.items():
    doc.getObject(name).Shape=s
    doc.getObject(name).ViewObject.DisplayMode='Flat Lines'
doc.recompute();Gui.Selection.clearSelection();doc.save()
checked={}
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml'));newxml=ET.fromstring(after.read('Document.xml'))
    for name in [o.Name for o in others]:
        a=oldxml.find("./ObjectData/Object[@name='%s']"%name);b=newxml.find("./ObjectData/Object[@name='%s']"%name)
        p="./Properties/Property[@name='Shape']/Part"
        x=before.read(a.find(p).attrib['file']).split();y=after.read(b.find(p).attrib['file']).split()
        assert len(x)==len(y),name
        for i,j in zip(x,y):
            if i==j or (i,j) in ((b'0101000',b'0111000'),(b'0111000',b'0101000')):continue
            assert abs(float(i)-float(j))<1e-12,name
        p="./Properties/Property[@name='Placement']/PropertyPlacement"
        assert a.find(p).attrib==b.find(p).attrib,name
    for name in shapes:
        node=newxml.find("./ObjectData/Object[@name='%s']"%name)
        p=node.find("./Properties/Property[@name='Shape']/Part").attrib['file']
        tmp=out/'verify.brp';tmp.write_bytes(after.read(p));s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-shapes[name].Volume)<1e-6
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume,'faces_before':before_faces[name],'faces_after':len(s.Faces),'refine_applied':refined[name]}
report={'change':'Fill 8 former board TPU pockets and 2 battery crossbar latch slots; refine coplanar seams where valid. Preserve main holder geometry, openings, screws and electronics.','changes':checks,'saved_shells':checked,'unchanged_other_objects':len(others),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitations':'No TPU compensation remains in these filled pockets; holding force/fit untested. Main corner guides remain; this does not remove all guides.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
