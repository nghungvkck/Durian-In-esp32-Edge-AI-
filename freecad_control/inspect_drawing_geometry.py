from pathlib import Path
import FreeCAD as App
import Part, TechDraw, json
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
P=ROOT/'3D/Enclosure_Center_Slot_D50/Enclosure_Center_Slot_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==P)
out=P.parent/'Technical_Drawing'; out.mkdir(exist_ok=True)
s=d.Rear_half.Shape.fuse(d.Front_half.Shape)
svg=TechDraw.projectToSVG(s,App.Vector(0,1,0))
(out/'projection_sample.svg').write_text(svg,encoding='utf-8')
circles={}
for name in ('Rear_half','Front_half'):
    rows=[]
    for f in d.getObject(name).Shape.Faces:
        sf=f.Surface
        if isinstance(sf,Part.Cylinder):
            rows.append({'r':sf.Radius,'axis':list(sf.Axis),'center':list(sf.Center),'bounds':[f.BoundBox.XMin,f.BoundBox.XMax,f.BoundBox.YMin,f.BoundBox.YMax,f.BoundBox.ZMin,f.BoundBox.ZMax]})
    circles[name]=rows
(out/'cylindrical_faces.json').write_text(json.dumps(circles,indent=2),encoding='utf-8')
result={'sample':svg[:3500],'cylinders':{n:len(v) for n,v in circles.items()},'objects':[(o.Name,o.TypeId) for o in d.Objects]}
