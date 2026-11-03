from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
import math
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
for obj in doc.Objects:
    obj.Visibility=obj.Name.startswith('Preview_')
    if obj.Name in ('Front_half','Rear_half'): obj.ViewObject.DisplayMode='Flat Lines'
view=Gui.activeDocument().activeView()
view.setCameraType('Orthographic')
camera=view.getCameraOrientation()
node=view.getCameraNode()
node.orientation.setValue(coin.SbRotation(coin.SbVec3f(1,0,0),-math.pi/2))
node.position.setValue(0,200,68)
node.height.setValue(155)
result={'view':'Rear view of separated shells; front screw heads and rear hex nuts face camera','saved':False}
