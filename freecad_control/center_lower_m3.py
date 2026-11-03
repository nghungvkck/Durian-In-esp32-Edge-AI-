"""Replace side M2 with centered M3; extend lower cavity by 10 mm."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
import Part,json,zipfile,hashlib,shutil
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
source=path.parent/'Lower_Screw/D36_before_lower_screw.FCStd'
out=path.parent/'Centered_Lower_M3';out.mkdir(exist_ok=True)
backup=out/'D36_before_centering_lower_M3.FCStd'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
assert not backup.exists() and doc.getObject('Screw_M2_Lower') and not doc.getObject('Screw_M3_Lower'),'Unexpected input'
assert abs(doc.Front_half.Shape.Volume-27468.523031449844)<.001
assert abs(doc.Rear_half.Shape.Volume-28130.06449267957)<.001
shutil.copy2(path,backup)
V=App.Vector
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
base={}
with zipfile.ZipFile(source) as archive:
    xml=ET.fromstring(archive.read('Document.xml'))
    for name in ('Front_half','Rear_half'):
        node=xml.find("./ObjectData/Object[@name='%s']"%name)
        tmp=out/'source.brp';tmp.write_bytes(archive.read(node.find("./Properties/Property[@name='Shape']/Part").attrib['file']))
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1
        base[name]=s
assert abs(base['Front_half'].Volume-27343.764920126046)<.001
assert abs(base['Rear_half'].Volume-28013.129980176807)<.001
# The plane Z13 lies between switch terminals (end12.5) and first SD/battery parts (start15).
cut_z=13.;extension=10.;screw_z=18.
lower_box=box(-30,30,-30,30,-1,cut_z)
upper_box=box(-30,30,-30,30,cut_z,160)
ring=Part.makeCylinder(18,extension,V(0,0,cut_z)).cut(Part.makeCylinder(16,extension,V(0,0,cut_z)))
outer=Part.makeCylinder(18,146)
post=Part.makeCylinder(4.5,36,V(0,-18,screw_z),V(0,1,0)).common(outer)
bore=Part.makeCylinder(2,40,V(0,-20,screw_z),V(0,1,0))
head_pocket=Part.makeCylinder(3.1,8,V(0,13,screw_z),V(0,1,0))
import math
radius=5.9/math.sqrt(3)
pts=[V(radius*math.cos(math.radians(30+i*60)),-20,screw_z+radius*math.sin(math.radians(30+i*60))) for i in range(6)]
nut_pocket=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(V(0,5.9,0))
halves={};joints={}
for name,y0,y1 in (('Front_half',0,20),('Rear_half',-20,0)):
    mask=box(-25,25,y0,y1,-1,160)
    lower=base[name].common(lower_box)
    upper=base[name].common(upper_box);upper.translate(V(0,0,extension))
    wall=ring.common(mask)
    boss=post.common(mask)
    s=lower.fuse(upper).fuse(wall).fuse(boss).cut(bore)
    s=s.cut(head_pocket if name=='Front_half' else nut_pocket)
    assert s.isValid() and len(s.Solids)==1,name
    b=s.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<.001 and abs(b.ZLength-146)<.001
    halves[name]=s;joints[name]=boss.cut(bore).cut(head_pocket if name=='Front_half' else nut_pocket)
assert halves['Front_half'].common(halves['Rear_half']).Volume<1e-6
fixed=('SW1','SW1_Terminals')
retained=[o for o in doc.Objects if o.Name not in ('Front_half','Rear_half','Screw_M2_Lower','Nut_M2_Lower')]
proposed={};moves=[];signatures={}
for o in retained:
    s=o.Shape.copy();shift=0 if o.Name in fixed else extension
    if shift:s.translate(V(0,0,shift))
    proposed[o.Name]=s
    signatures[o.Name]=(o.Shape.Volume,o.Shape.Area,o.Placement.copy())
    moves.append({'name':o.Name,'delta_Z_mm':shift})
lower_screw=doc.Screw_M3_1.Shape.copy();lower_screw.translate(V(0,0,screw_z-111))
lower_nut=doc.Nut_M3_1.Shape.copy();lower_nut.translate(V(0,0,screw_z-111))
clearances=[]
for name,s in proposed.items():
    b=s.optimalBoundingBox(False,False)
    if b.ZMin>26:continue
    for half,joint in joints.items():
        volume=joint.common(s).Volume;distance=joint.distToShape(s)[0]
        assert volume<1e-6 and distance>.19,(half,name,volume,distance)
        clearances.append({'joint':half,'component':name,'distance_mm':distance})
    for hardware in (lower_screw,lower_nut):
        assert hardware.common(s).Volume<1e-6 and hardware.distToShape(s)[0]>.19,name
for shape in (lower_screw,lower_nut):
    assert shape.isValid() and len(shape.Solids)==1
    assert shape.common(halves['Front_half']).Volume<1e-6 and shape.common(halves['Rear_half']).Volume<1e-6
    assert shape.cut(outer).Volume<1e-6
assert lower_screw.common(lower_nut).Volume<1e-6
for name,s in halves.items():doc.getObject(name).Shape=s
for o in retained:
    if o.Name not in fixed:
        p=o.Placement.copy();p.Base=p.Base+V(0,0,extension);o.Placement=p
    v,a,p=signatures[o.Name]
    assert abs(o.Shape.Volume-v)<1e-6 and abs(o.Shape.Area-a)<1e-6,o.Name
    target=p.Base+(V(0,0,0) if o.Name in fixed else V(0,0,extension))
    assert (o.Placement.Base-target).Length<1e-8 and o.Placement.Rotation.isSame(p.Rotation,1e-9)
doc.removeObject('Screw_M2_Lower');doc.removeObject('Nut_M2_Lower')
for name,label,s in (('Screw_M3_Lower','Vít thân dưới M3 x 30 - giữa thân',lower_screw),('Nut_M3_Lower','Đai ốc M3 thân dưới',lower_nut)):
    o=doc.addObject('PartDesign::Feature',name);o.Shape=s;o.Label=label
    o.ViewObject.ShapeColor=(.73,.75,.78);o.ViewObject.DisplayMode='Flat Lines'
for o in doc.Objects:o.Visibility=True
for name in halves:doc.getObject(name).ViewObject.DisplayMode='Shaded'
doc.recompute();Gui.Selection.clearSelection()
view=Gui.activeDocument().activeView();view.setCameraType('Orthographic');node=view.getCameraNode()
rotation=App.Rotation(V(1,0,0),-90).multiply(App.Rotation(V(0,0,1),180))
node.orientation.setValue(coin.SbRotation(*rotation.Q));node.position.setValue(0,220,73);node.height.setValue(166)
doc.save()
checked={}
with zipfile.ZipFile(path) as archive:
    xml=ET.fromstring(archive.read('Document.xml'))
    for name in ('Front_half','Rear_half','Screw_M3_Lower','Nut_M3_Lower'):
        obj=xml.find("./ObjectData/Object[@name='%s']"%name)
        tmp=out/'verify.brp';tmp.write_bytes(archive.read(obj.find("./Properties/Property[@name='Shape']/Part").attrib['file']))
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-doc.getObject(name).Shape.Volume)<1e-6
        b=s.optimalBoundingBox(False,False)
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume,'bbox_mm':[b.XLength,b.YLength,b.ZLength]}
report={'case_diameter_length_mm':[36,146],'extension_mm':10,'extension_plane_Z_mm':13,'new_center_XZ_mm':[0,18],'all_screw_centers_XZ_mm':[[0,18],[0,121],[0,141]],'all_screws':'3 x M3 x 30 nominal, head D5.5 H3; simplified no helical threads','lower_bore_diameter_mm':4,'head_pocket_diameter_mm':6.2,'nut_pocket_AF_mm':5.9,'lower_compression_post_radius_mm':4.5,'removed':['Screw_M2_Lower','Nut_M2_Lower','offset lower M2 hole and side bosses'],'moves':moves,'clearances':clearances,'saved_BRep':checked,'object_count':len(doc.Objects),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup),'limitations':'Nominal model; fit, torque and print strength untested. No wires modeled; extra switch-to-boards separation needs wiring allowance.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
