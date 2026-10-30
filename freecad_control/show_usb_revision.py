from pathlib import Path
import json, math
import FreeCAD as App
import FreeCADGui as Gui
import Part
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
newpath=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
oldpath=ROOT/'3D/Enclosure_Center_Slot_D50/Enclosure_Center_Slot_D50.FCStd'
new=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==newpath)
old=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==oldpath)
OUT=newpath.parent
n=App.Vector(-.75,1,.18); n.normalize()
r=App.Vector(0,0,1).cross(n); r.normalize(); u=n.cross(r)
def view(d,detail=False):
 App.setActiveDocument(d.Name)
 d.Front_half.Visibility=False; d.Rear_half.Visibility=True
 d.Charge_plug_envelope.Visibility=False; d.Code_plug_envelope.Visibility=False
 v=Gui.activeDocument().activeView(); v.setCameraType('Orthographic')
 v.setCameraOrientation(App.Rotation(r,u,n,'ZXY').Q); v.fitAll()
 if detail:
  c=v.getCameraNode(); focus=App.Vector(-8,-6,126); pos=focus+n*300
  c.position.setValue(pos.x,pos.y,pos.z); c.focalDistance.setValue(300); c.height.setValue(72)
  c.nearDistance.setValue(1); c.farDistance.setValue(1000)
 return v
view(old,True).saveImage(str(OUT/'usb_before.png'),1400,1600,'White')
view(new,True).saveImage(str(OUT/'usb_after.png'),1400,1600,'White')
view(new).saveImage(str(OUT/'usb_inside_full.png'),1200,1800,'White')
new.Front_half.Visibility=True
viewnew=Gui.activeDocument().activeView()
viewnew.saveImage(str(OUT/'usb_closed.png'),1200,1800,'White')
view(new,True)
checks={}
for board,plug,oldmouth in [('IP5306','Charge_plug_envelope',-13),('ESP32_C3','Code_plug_envelope',-12)]:
 mouth=new.getObject(board).Shape.BoundBox.XMin
 recess=math.sqrt(25**2-5.5**2)-abs(mouth)
 volumes={s:new.getObject(s).Shape.common(new.getObject(plug).Shape).Volume for s in ('Rear_half','Front_half')}
 assert max(volumes.values())<.001
 checks[board]={'old_mouth_x_mm':oldmouth,'mouth_x_mm':mouth,'recess_at_centerline_mm':recess,'plug_overmold_mm':[20,8,12],'plug_shell_intersection_mm3':volumes}
srcshape=old.Front_half.Shape
keyregion=Part.makeBox(20,8,40,App.Vector(-10,17,128))
assert srcshape.common(keyregion).cut(new.Front_half.Shape).Volume<.001,'Front button cradle changed'
checks['button_cradle_unchanged']=True
checks['notes']=['USB connector faces and cable envelope are nominal; real cable and board still require fit testing.','Local PCB corner relief has about 1.2 mm minimum radial wall by the clearance box envelope.']
(OUT/'usb_fit.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
result=checks
