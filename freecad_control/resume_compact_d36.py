from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
p=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\3D\Enclosure_Compact_Layout_D36\Compact_Layout_D36.FCStd')
d=next((d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(p).casefold()),None)
if d is None:d=App.openDocument(str(p))
assert d.getObject('Front_half') and d.getObject('Rear_half')
App.setActiveDocument(d.Name)
for o in d.Objects:
 if hasattr(o,'ViewObject'):o.Visibility=o.Name in ['Preview_Rear_Separated','Preview_Front_Separated']
v=Gui.activeDocument().activeView();v.viewFront();v.fitAll()
result={'file':d.FileName,'dimensions_mm':[36,136],'wall_mm':2,'mic_ic_height_mm':2,'status':'Two-half layout prototype, no print-ready STL','view':'Separated view links only; Front_half/Rear_half retain assembly coordinates'}
