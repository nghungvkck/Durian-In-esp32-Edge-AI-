from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
p=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\3D\Enclosure_Compact_Layout_D40\Compact_Layout_D40.FCStd')
d=next((d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(p).casefold()),None)
if d is None:d=App.openDocument(str(p))
assert d.getObject('Envelope_Rear_REFERENCE') and d.getObject('Battery')
App.setActiveDocument(d.Name)
d.Envelope_Rear_REFERENCE.Visibility=True
d.Envelope_Rear_REFERENCE.ViewObject.Transparency=85
d.Envelope_Front_REFERENCE.Visibility=False
v=Gui.activeDocument().activeView();v.viewAxonometric();v.fitAll()
result={'file':d.FileName,'status':'PLACEMENT STUDY ONLY; NO PRINTABLE STL','dimensions_mm':[40,136],'source_D50_unchanged':True}
