"""Revise the accepted assembly: translate charger/ESP USB mouths to X=-23."""
from pathlib import Path
import json, math, shutil
import FreeCAD as App
import FreeCADGui as Gui
import Part
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
SOURCE=ROOT/'3D/Enclosure_Center_Slot_D50/Enclosure_Center_Slot_D50.FCStd'
OUT=ROOT/'3D/Enclosure_USB_Near_Wall_D50'
src=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==SOURCE)
assert not OUT.exists(), 'Revision already exists; inspect rather than rerun'
V=App.Vector
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,V(x,y,z))
outer=Part.makeCylinder(25,201)
wall=outer.cut(Part.makeCylinder(22,165,V(0,0,3)))
rear=src.Rear_half.Shape.copy(); front=src.Front_half.Shape.copy()
for name,dx,z,h,xlim in [('IP5306',-10,98,24,16),('ESP32_C3',-11,129,22,15)]:
    region=box(-xlim,-30,z,2*xlim,30,h)
    support=src.Rear_half.Shape.common(region).cut(wall)
    support.translate(V(dx,0,0)); support=support.common(outer)
    rear=rear.cut(region).fuse(wall.common(region)).fuse(support)
    # Re-anchor the relocated PCB back supports to the curved rear wall.
    for x in ((-11+dx,9.6+dx) if name=='IP5306' else (-9.7+dx,8.6+dx)):
        strut=box(x,-25,z+2.4,2.4,16.85,h-4.8).common(outer)
        rear=rear.fuse(strut)
    # Remove the old front pressure fingers; the rear tray retains the PCB.
    # Preserve the outer wall, seam hardware and unrelated front button cradle.
    finger_region=box(-13 if name=='IP5306' else -11,-7,z,27 if name=='IP5306' else 24,32,h)
    # Only remove original fingers, not all internals: each lies outside X±8.
    for left,right in ((-13.3,-9.5),(10.5,13.5)) if name=='IP5306' else ((-10.8,-8.4),(9.1,12.1)):
        r=box(left,-7,z,right-left,32 if name=='IP5306' else 23.8,h)
        front=front.cut(r).fuse(wall.common(r).common(box(-30,0,0,60,30,201)))
    # Pocket for the PCB corners near the curved side, with 0.3 mm side gap.
    b=src.getObject(name).Shape.BoundBox
    pcb_min=-12 if name=='IP5306' else -10.7
    clearance=box(pcb_min+dx-.3,-8.4,b.ZMin-.3,b.XMax-pcb_min+.6,1.65,b.ZLength+.6)
    rear=rear.cut(clearance)
    # The existing 12 x 15 USB access wells stay aligned in Y/Z.
    mouth=box(-31,-11.5,(110 if name=='IP5306' else 139.9016)-7.5,14,12,15)
    rear=rear.cut(mouth); front=front.cut(mouth)
slot=box(-10,-1.5,3,20,3,199)
rear=rear.cut(slot); front=front.cut(slot)
for n,s in [('Rear_half',rear),('Front_half',front)]:
    assert s.isValid() and len(s.Solids)==1 and s.Volume>70000, (n,s.isValid(),len(s.Solids),s.Volume)
failed=App.getDocument('Enclosure_USB_Near_Wall_D50')
if failed is not None and not failed.FileName: App.closeDocument(failed.Name)
doc=App.newDocument('Enclosure_USB_Near_Wall_D50')
for old in src.Objects: doc.copyObject(old,False)
doc.Rear_half.Shape=rear; doc.Front_half.Shape=front
for name,dx in [('IP5306',-10),('ESP32_C3',-11),('Charge_plug_envelope',-10),('Code_plug_envelope',-11)]:
    obj=doc.getObject(name); placement=obj.Placement
    placement.Base+=V(dx,0,0); obj.Placement=placement
netlist=json.loads((SOURCE.parent/'wire_netlist.json').read_text())
for wire in netlist:
    n=wire['name']; pts=wire['points_mm']
    if n in ('BAT_plus','BAT_minus'): pts[-1][0]-=10
    elif n=='Boost_to_switch':
        pts=[[-16,-2.7,113],[-16,8,113],[-6,8,113],[-6,16,113],[-6,16,12.3],[-3,16,12.3]]
    elif n=='Switch_to_ESP':
        pts=pts[:5]+[[14,0,153],[-20.251,0,153],[-20.251,0,147.4036],[-20.251,-6.1,147.4036]]
    elif n=='Ground_to_ESP':
        pts=[[-3,-2.7,113],[-3,14,113],[15,14,113],[15,14,147.4036],[15,2,147.4036],[-17.696,2,147.4036],[-17.696,-6.1,147.4036]]
    elif n.startswith('SPI_'):
        pts[-1][0]-=11; pts[-2][0]-=11
    else: continue
    wire['points_mm']=pts
    segments=[]
    for a,b in zip(pts,pts[1:]):
        a,b=V(*a),V(*b); delta=b-a
        if delta.Length>1e-7: segments.append(Part.makeCylinder(wire['diameter_mm']/2,delta.Length,a,delta))
    segments += [Part.makeSphere(wire['diameter_mm']/2,V(*p)) for p in pts[1:-1]]
    shape=segments[0].multiFuse(segments[1:])
    assert shape.isValid() and len(shape.Solids)==1, n
    doc.getObject(n).Shape=shape
    doc.getObject(n).Placement=App.Placement()
    wire['cut_length_mm']=math.ceil(sum((V(*a)-V(*b)).Length for a,b in zip(pts,pts[1:]))+15)
doc.recompute()
OUT.mkdir()
(OUT/'wire_netlist.json').write_text(json.dumps(netlist,indent=2),encoding='utf-8')
shutil.copyfile(SOURCE.parent/'button_module_spec.json',OUT/'button_module_spec.json')
doc.saveAs(str(OUT/'Enclosure_USB_Near_Wall_D50.FCStd'))
App.setActiveDocument(doc.Name)
doc.Front_half.Visibility=False; doc.Rear_half.Visibility=True
doc.Charge_plug_envelope.Visibility=False; doc.Code_plug_envelope.Visibility=False
Gui.activeDocument().activeView().viewAxonometric(); Gui.activeDocument().activeView().fitAll()
result={'file':doc.FileName,'mouth_x_mm':-23,'shift_x_mm':{'IP5306':-10,'ESP32_C3':-11},'center_recess_mm':round(math.sqrt(25**2-5.5**2)-23,3),'shell_volumes_mm3':{n:doc.getObject(n).Shape.Volume for n in ('Rear_half','Front_half')}}
