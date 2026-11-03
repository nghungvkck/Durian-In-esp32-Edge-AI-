"""Add one lower side M2 joint with integral compression bosses."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part,math,json,zipfile,hashlib,shutil
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Lower_Screw';out.mkdir(exist_ok=True)
backup=out/'D36_before_lower_screw.FCStd'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
assert not doc.getObject('Screw_M2_Lower'),'Already applied; inspect before retry'
if backup.exists():
    assert hashlib.sha256(backup.read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest(),'Backup differs from current input'
assert abs(doc.Front_half.Shape.Volume-27343.764920126046)<.001
assert abs(doc.Rear_half.Shape.Volume-28013.129980176807)<.001
if not backup.exists():shutil.copy2(path,backup)
V=App.Vector;x=14.;z=8.5
def hexprism(af,y,h):
    r=af/math.sqrt(3)
    points=[V(x+r*math.cos(math.radians(30+i*60)),y,z+r*math.sin(math.radians(30+i*60))) for i in range(6)]
    return Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(V(0,h,0))
envelope=Part.makeCylinder(18,136)
bore=Part.makeCylinder(1.2,40,V(x,-20,z),V(0,1,0))
head_pocket=Part.makeCylinder(2.2,14,V(x,6,z),V(0,1,0))
nut_pocket=hexprism(4.4,-20,14)
front_boss=Part.makeBox(6.2,18,7.4,V(11.8,0,5.3)).common(envelope)
rear_boss=Part.makeBox(6.2,18,7.4,V(11.8,-18,5.3)).common(envelope)
front=doc.Front_half.Shape.fuse(front_boss).cut(bore).cut(head_pocket)
rear=doc.Rear_half.Shape.fuse(rear_boss).cut(bore).cut(nut_pocket)
shaft=Part.makeCylinder(1,14,V(x,-8,z),V(0,1,0))
head=Part.makeCylinder(1.9,2,V(x,6,z),V(0,1,0))
screw=shaft.fuse(head).cut(hexprism(1.5,7,1.5))
nut=hexprism(4,-7.6,1.6).cut(Part.makeCylinder(1,2,V(x,-7.8,z),V(0,1,0)))
others=[o for o in doc.Objects if o.Name not in ('Front_half','Rear_half')]
checks=[]
for name,old,new in (('Front_half',doc.Front_half.Shape,front),('Rear_half',doc.Rear_half.Shape,rear)):
    assert new.isValid() and len(new.Solids)==1,name
    b=new.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<.001 and abs(b.ZLength-136)<.001
    addition=new.cut(old)
    distances=[]
    for obj in others:
        a=addition.BoundBox;c=obj.Shape.BoundBox
        if not all(getattr(a,k+'Max')>=getattr(c,k+'Min') and getattr(c,k+'Max')>=getattr(a,k+'Min') for k in ('X','Y','Z')):continue
        assert addition.common(obj.Shape).Volume<1e-6,name+' boss clashes '+obj.Name
        distance=addition.distToShape(obj.Shape)[0]
        assert distance>.19,name+' boss too near '+obj.Name
        distances.append({'component':obj.Name,'distance_mm':distance})
    checks.append({'shell':name,'added_boss_volume_mm3':addition.Volume,'component_clearances':distances})
assert front.common(rear).Volume<1e-6, 'Shell/boss overlap'
for name,s in (('Screw_M2_Lower',screw),('Nut_M2_Lower',nut)):
    assert s.isValid() and len(s.Solids)==1
    assert s.common(front).Volume<1e-6 and s.common(rear).Volume<1e-6
    for obj in others:
        if obj.Shape.BoundBox.ZMin>13:continue
        assert s.common(obj.Shape).Volume<1e-6,name+' clashes '+obj.Name
        assert s.distToShape(obj.Shape)[0]>.19,name+' too near '+obj.Name
assert screw.common(nut).Volume<1e-6
# Head and nut completely within the original cylindrical envelope.
assert screw.cut(envelope).Volume<1e-6 and nut.cut(envelope).Volume<1e-6
doc.Front_half.Shape=front;doc.Rear_half.Shape=rear
for name,label,s in (('Screw_M2_Lower','Vít thân dưới M2 x 14',screw),('Nut_M2_Lower','Đai ốc thân dưới M2',nut)):
    o=doc.addObject('PartDesign::Feature',name);o.Label=label;o.Shape=s
    o.addProperty('App::PropertyString','ModelNote').ModelNote='Nominal metal hardware; simplified cylindrical thread envelope, not a printed part'
    o.ViewObject.ShapeColor=(.73,.75,.78);o.Visibility=True
    o.ViewObject.DisplayMode='Flat Lines'
for name in ('Front_half','Rear_half'):
    doc.getObject(name).ViewObject.DisplayMode='Shaded'
doc.recompute();Gui.Selection.clearSelection();doc.save()
checked={}
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml'));newxml=ET.fromstring(after.read('Document.xml'))
    for obj in others:
        name=obj.Name
        a=oldxml.find("./ObjectData/Object[@name='%s']"%name);b=newxml.find("./ObjectData/Object[@name='%s']"%name)
        p="./Properties/Property[@name='Shape']/Part"
        aa=before.read(a.find(p).attrib['file']).split();bb=after.read(b.find(p).attrib['file']).split()
        assert len(aa)==len(bb),name
        for i,j in zip(aa,bb):
            if i==j or (i,j) in ((b'0101000',b'0111000'),(b'0111000',b'0101000')):continue
            assert abs(float(i)-float(j))<1e-12,name
        p="./Properties/Property[@name='Placement']/PropertyPlacement"
        assert a.find(p).attrib==b.find(p).attrib,name+' placement'
    for name in ('Front_half','Rear_half','Screw_M2_Lower','Nut_M2_Lower'):
        node=newxml.find("./ObjectData/Object[@name='%s']"%name)
        tmp=out/'verify.brp';tmp.write_bytes(after.read(node.find("./Properties/Property[@name='Shape']/Part").attrib['file']))
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-doc.getObject(name).Shape.Volume)<1e-6
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume}
report={'center_XZ_mm':[x,z],'axis':'+Y','screw':'M2 x 14, head D3.8 H2, simplified no helical thread','nut':'M2 AF4 H1.6, simplified no helical thread','new_bore_diameter_mm':2.4,'head_pocket_diameter_mm':4.4,'head_seat_Y_mm':6,'head_top_Y_mm':8,'nut_pocket_AF_mm':4.4,'nut_seat_Y_mm':-6,'nut_outer_Y_mm':-7.6,'screw_tip_Y_mm':-8,'integral_boss_envelope_XYZ_mm':[11.8,18,-18,18,5.3,12.7],'compression':'Two integral side bosses meet at Y0; avoids clamping across an unsupported hollow gap.','hardware_inside_D36_envelope':True,'checks':checks,'unchanged_other_objects':len(others),'saved_BRep':checked,'object_count':len(doc.Objects),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitations':'Nominal hardware; print fit, material, nut capture before insertion, torque and real joint strength untested. Existing M3 upper screws unchanged.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
