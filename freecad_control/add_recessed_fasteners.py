"""Self-contained edit of the current D36; run only through Windows bridge."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part, math, json, shutil, hashlib
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Recessed_Fasteners'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
assert not doc.getObject('Screw_M3_1'), 'Already applied; do not rerun'
front,rear=doc.Front_half,doc.Rear_half
assert abs(front.Shape.Volume-27505.932516)<.001 and abs(rear.Shape.Volume-28127.278876)<.001, 'Unexpected source geometry'
out.mkdir(exist_ok=True)
backup=out/'D36_before_recessed_fasteners.FCStd'
if backup.exists():
    assert hashlib.sha256(backup.read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest(), 'Backup differs from input'
else:
    shutil.copy2(path,backup)
sources={o.Name:(o.Shape.copy(),str(o.Placement)) for o in doc.Objects if hasattr(o,'Shape') and o.Name not in ('Front_half','Rear_half') and not o.Name.startswith('Preview_')}
V=App.Vector
def hexprism(af,y,z,h):
    r=af/math.sqrt(3)
    p=[V(r*math.cos(math.radians(30+60*i)),y,z+r*math.sin(math.radians(30+60*i))) for i in range(6)]
    return Part.Face(Part.Wire(Part.makePolygon(p+[p[0]]).Edges)).extrude(V(0,h,0))
f=front.Shape.copy(); r=rear.Shape.copy(); hardware=[]
for i,z in enumerate((111.,131.),1):
    # Head seat Y=13.0, top of M3 head Y=16.0; original bore stays R2.
    f=f.cut(Part.makeCylinder(3.1,7,V(0,13,z),V(0,1,0)))
    # Open from rear exterior, flats constrain nut rotation; seat Y=-14.1.
    r=r.cut(hexprism(5.9,-20,z,5.9))
    shaft=Part.makeCylinder(1.5,30,V(0,-17,z),V(0,1,0))
    head=Part.makeCylinder(2.75,3,V(0,13,z),V(0,1,0))
    screw=shaft.fuse(head).cut(hexprism(2.5,14.5,z,2.0))
    nut=hexprism(5.5,-16.5,z,2.4).cut(Part.makeCylinder(1.5,3,V(0,-16.8,z),V(0,1,0)))
    hardware.extend([(f'Screw_M3_{i}',screw),(f'Nut_M3_{i}',nut)])
for shape in (f,r):
    assert shape.isValid() and len(shape.Solids)==1
    b=shape.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<.001 and abs(b.ZLength-136)<.001
assert f.common(r).Volume<1e-6
checks=[]
for name,s in hardware:
    assert s.isValid() and len(s.Solids)==1
    assert s.common(f).Volume<1e-6 and s.common(r).Volume<1e-6, name+' clashes shell'
    for other,(original,placement) in sources.items():
        if other.startswith('TPU_') and other.endswith('_Print'): continue
        assert s.common(original).Volume<1e-6, name+' clashes '+other
    checks.append({'name':name,'valid':True,'solids':1,'shell_intersection_mm3':[s.common(f).Volume,s.common(r).Volume]})
# Two original 4 mm through-bore portions must survive below the head/nut pockets.
for sh,cy in ((f,5),(r,-10)):
    for z in (111.,131.):
        bore=Part.makeCylinder(2,4,V(0,cy,z),V(0,1,0))
        assert sh.common(bore).Volume<1e-6
front.Shape=f; rear.Shape=r
for name,s in hardware:
    o=doc.addObject('PartDesign::Feature',name); o.Shape=s
    o.Label=('Vít M3 x 30 - ' if name.startswith('Screw') else 'Đai ốc lục giác M3 - ')+name.rsplit('_',1)[1]
    o.addProperty('App::PropertyString','ModelNote').ModelNote='Nominal simplified metal hardware, no helical thread; not a printed part'
    o.ViewObject.ShapeColor=(0.73,0.75,0.78)
    o.ViewObject.DisplayMode='Flat Lines'
    link=doc.addObject('App::Link','Preview_'+name)
    link.setLink(o)
    link.LinkPlacement=(doc.Preview_Front_Separated if name.startswith('Screw') else doc.Preview_Rear_Separated).Placement
for o in doc.Objects:
    o.Visibility=o.Name.startswith('Preview_')
front.ViewObject.DisplayMode='Flat Lines'; rear.ViewObject.DisplayMode='Flat Lines'
doc.recompute()
for name,(s,pl) in sources.items():
    o=doc.getObject(name)
    assert str(o.Placement)==pl and abs(s.Volume-o.Shape.Volume)<1e-7, 'Changed reference '+name
view=Gui.activeDocument().activeView(); view.viewAxonometric(); view.fitAll(); Gui.Selection.clearSelection()
doc.recompute()
doc.save()
# Re-read serialized BRep without opening/modifying another GUI document.
import zipfile, tempfile
with zipfile.ZipFile(path) as archive:
    import xml.etree.ElementTree as ET
    xml=ET.fromstring(archive.read('Document.xml'))
    checked={}
    for node in xml.findall('./ObjectData/Object'):
        name=node.attrib['name']
        if name not in ('Front_half','Rear_half',*[n for n,s in hardware]): continue
        prop=node.find("./Properties/Property[@name='Shape']/Part")
        filename=prop.attrib['file']
        tmp=out/(name+'_verify.brp'); tmp.write_bytes(archive.read(filename))
        shape=Part.Shape(); shape.read(str(tmp)); tmp.unlink()
        expected=doc.getObject(name).Shape
        assert shape.isValid() and len(shape.Solids)==1
        assert abs(shape.Volume-expected.Volume)<1e-7
        assert all(abs(a-b)<1e-7 for a,b in zip((shape.BoundBox.XMin,shape.BoundBox.YMin,shape.BoundBox.ZMin,shape.BoundBox.XMax,shape.BoundBox.YMax,shape.BoundBox.ZMax),(expected.BoundBox.XMin,expected.BoundBox.YMin,expected.BoundBox.ZMin,expected.BoundBox.XMax,expected.BoundBox.YMax,expected.BoundBox.ZMax)))
        checked[name]={'valid':True,'solids':len(shape.Solids),'volume_mm3':shape.Volume}
assert len(checked)==6
# Exact serialized payload and placement comparison avoids expensive identity Booleans.
with zipfile.ZipFile(backup) as before, zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml'))
    newxml=ET.fromstring(after.read('Document.xml'))
    for name in sources:
        oldnode=oldxml.find("./ObjectData/Object[@name='%s']" % name)
        newnode=newxml.find("./ObjectData/Object[@name='%s']" % name)
        oldfile=oldnode.find("./Properties/Property[@name='Shape']/Part").attrib['file']
        newfile=newnode.find("./Properties/Property[@name='Shape']/Part").attrib['file']
        assert before.read(oldfile)==after.read(newfile), 'Serialized reference changed '+name
        assert oldnode.find("./Properties/Property[@name='Placement']/PropertyPlacement").attrib==newnode.find("./Properties/Property[@name='Placement']/PropertyPlacement").attrib, 'Saved placement changed '+name
report={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup),'hole_diameter_mm':4,'centers_XZ_mm':[[0,111],[0,131]],'screw':'2 x M3 x 30, nominal cylindrical socket head D5.5 H3, simplified unthreaded','head_seat_Y_mm':13,'head_top_Y_mm':16,'head_pocket_diameter_mm':6.2,'nut':'2 x M3, AF5.5 H2.4, simplified unthreaded','nut_pocket_AF_mm':5.9,'nut_seat_Y_mm':-14.1,'nut_outer_Y_mm':-16.5,'tip_Y_mm':-17,'unchanged_reference_count':len(sources),'hardware_checks':checks,'serialized_BRep':checked,'limits':'Nominal model; threads, tolerances, nut insertion/retention under real load and printed fit not tested. Nut is constrained against rotation; not retained against falling out before screw engagement.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
