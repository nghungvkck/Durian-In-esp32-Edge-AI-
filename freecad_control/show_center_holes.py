"""Verify the current assembly and display the centered front holes."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
p=ROOT/'freecad_control/resume_latest.py'
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),globals())
assembly.Front_half.Visibility=True
v=Gui.activeDocument().activeView()
n=App.Vector(0,1,0); right=App.Vector(0,0,1).cross(n); up=n.cross(right)
v.setCameraOrientation(App.Rotation(right,up,n,'ZXY').Q)
v.setCameraType('Orthographic'); v.fitAll(); Gui.Selection.clearSelection()
result['view']='Front elevation, both halves shown; two diameter-4 holes on X0 centerline, pitch20.'
