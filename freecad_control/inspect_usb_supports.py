from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
p=ROOT/'3D/Enclosure_Center_Slot_D50/Enclosure_Center_Slot_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==p)
def bb(s):
 b=s.BoundBox
 return [round(v,3) for v in (b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax)]
result={}
for name,z,h in [('IP5306',98,24),('ESP32_C3',129,22)]:
 region=Part.makeBox(36,24,h,App.Vector(-18,-23,z))
 shapes={}
 for half in ('Rear_half','Front_half'):
  s=d.getObject(half).Shape.common(region).common(Part.makeCylinder(21.95,201))
  shapes[half]={'volume':s.Volume,'bounds':bb(s),'solids':[bb(t) for t in s.Solids]}
 result[name]=shapes
