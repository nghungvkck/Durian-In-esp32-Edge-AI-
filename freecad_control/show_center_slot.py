from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
p=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==p)
App.setActiveDocument(d.Name)
d.Rear_half.Visibility=True
d.Front_half.Visibility=True
Gui.Selection.clearSelection()
v=Gui.activeDocument().activeView()
v.setCameraType('Orthographic'); v.viewTop(); v.fitAll()
c=v.getCameraNode(); c.height.setValue(65)
v.saveImage(str(p.parent/'center_slot_top.png'),1200,1000,'White')
result={'active':d.Name,'view':'Top, both shell halves visible','slot_mm':[20,3]}
