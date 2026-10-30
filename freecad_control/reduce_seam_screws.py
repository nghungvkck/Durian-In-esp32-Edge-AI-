"""Reduce the existing five seam-fastener levels to three, keeping internals."""
from pathlib import Path
import shutil
import FreeCAD as App
import FreeCADGui as Gui
import Part
V=App.Vector
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
SOURCE=ROOT/'3D/Enclosure_Center_Holes_D50/Enclosure_Center_Holes_D50.FCStd'
OUT=ROOT/'3D/Enclosure_Three_Seam_Screws_D50'
assert not (OUT/'Enclosure_Three_Seam_Screws_D50.FCStd').exists(), 'Revision already saved; inspect before repeating'
draft=next((d for d in App.listDocuments().values() if d.Label=='Enclosure_Three_Seam_Screws_D50'),None)
assert draft is None or not draft.FileName, 'Saved revision already open'
source=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==SOURCE),None)
if source is None: source=App.openDocument(str(SOURCE))
doc=draft or App.newDocument('Enclosure_Three_Seam_Screws_D50'); doc.Label='Enclosure_Three_Seam_Screws_D50'
for old in source.Objects:
    if old.TypeId!='Part::Feature': continue
    o=doc.getObject(old.Name) or doc.addObject('Part::Feature',old.Name); o.Label=old.Label; o.Shape=old.Shape.copy()
    o.ViewObject.ShapeColor=old.ViewObject.ShapeColor; o.ViewObject.LineColor=old.ViewObject.LineColor
    for p in ('DesignNote','DimensionBasis'):
        if p in old.PropertiesList:
            if p not in o.PropertiesList: o.addProperty('App::PropertyString',p,'Design')
            setattr(o,p,getattr(old,p))
outer=Part.makeCylinder(25,201)
inner=Part.makeCylinder(22,165,V(0,0,3))
wall=outer.cut(inner)
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,V(x,y,z))
for name,y in (('Rear_half',-30),('Front_half',0)):
    shape=doc.getObject(name).Shape.copy()
    for x in (-21,21):
        for z in (43,127):
            # Replace the local boss/wall region with plain wall. A 0.1 mm
            # overlap avoids coincident Boolean slivers at the patch borders.
            region=box(x-3.5,-30,z-3.6,7,60,7.2)
            shape=shape.cut(region)
            patch=wall.common(box(x-3.6,y,z-3.7,7.2,30,7.4))
            shape=shape.fuse(patch)
            if name=='Rear_half':
                tongue_x=-23.7 if x<0 else 22.7
                shape=shape.fuse(box(tongue_x,-.25,z-3.7,1,1.25,7.4))
    if name=='Front_half':
        # Wall restoration must leave the existing mating-tongue grooves clear.
        for x in (-23.95,22.45): shape=shape.cut(box(x,-.1,3.7,1.5,1.4,163.6))
    # Rear's valid fused shape triggers an OCC refinement bug (void Bnd_Box).
    # Refinement only removes redundant edges; keep the checked BRep there.
    if name=='Front_half': shape=shape.removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>70000, name
    doc.getObject(name).Shape=shape
    doc.getObject(name).DesignNote+=' Seam screws reduced to three levels per side: Z14/97/166 at X+/-21. Bosses and bores at Z43/127 removed and wall closed. Six seam screws total.'
assert doc.Rear_half.Shape.common(doc.Front_half.Shape).Volume<.02
for old in source.Objects:
    if old.TypeId!='Part::Feature' or old.Name in ('Rear_half','Front_half'): continue
    new=doc.getObject(old.Name)
    assert len(old.Shape.Vertexes)==len(new.Shape.Vertexes) and all((a.Point-b.Point).Length<.000001 for a,b in zip(old.Shape.Vertexes,new.Shape.Vertexes))
OUT.mkdir(exist_ok=True)
for filename in ('wire_netlist.json','button_module_spec.json'):
    shutil.copyfile(SOURCE.parent/filename,OUT/filename)
doc.recompute(); App.setActiveDocument(doc.Name)
for o in doc.Objects:
    o.Visibility=o.Name not in ('Charge_plug_envelope','Code_plug_envelope','Mic_Edge_Screw_L','Mic_Edge_Screw_R','Key_Screw_55','Key_Screw_85')
Gui.Selection.clearSelection()
doc.saveAs(str(OUT/'Enclosure_Three_Seam_Screws_D50.FCStd'))
result={'file':doc.FileName,'seam_screws':{'per_side':3,'total':6,'x_mm':[-21,21],'kept_z_mm':[14,97,166],'removed_z_mm':[43,127]},'volumes_mm3':{n:doc.getObject(n).Shape.Volume for n in ('Rear_half','Front_half')}}
