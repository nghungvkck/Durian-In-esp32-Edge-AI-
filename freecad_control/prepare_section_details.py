from pathlib import Path
import FreeCAD as App
import Part, TechDraw
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
p=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==p)
whole=d.Rear_half.Shape.fuse(d.Front_half.Shape)
half=whole.common(Part.makeBox(30,60,205,App.Vector(0,-30,-1)))
sec=Part.makeCompound([f for f in half.Faces if f.BoundBox.XLength<.00001 and abs(f.BoundBox.XMin)<.00001])
for name,z,dz in [('cap_section',168,33),('floor_section',0,15)]:
    s=sec.common(Part.makeBox(2,60,dz,App.Vector(-1,-30,z)))
    mat=App.Matrix(0,-1,0,0,0,0,1,0,-1,0,0,0,0,0,0,1)
    s.transformShape(mat)
    (p.parent/'Technical_Drawing'/(name+'.svgfrag')).write_text(TechDraw.projectToSVG(s,App.Vector(0,0,1)),encoding='utf-8')
result={'details':['cap_section','floor_section']}
