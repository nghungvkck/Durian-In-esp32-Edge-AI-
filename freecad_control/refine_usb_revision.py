"""Resolve routed-wire crossings and retain the existing six seam bores."""
from pathlib import Path
import json, math
import FreeCAD as App
import Part
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
P=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==P)
V=App.Vector
for x in (-21,21):
 for z in (14,97,166):
  d.Rear_half.Shape=d.Rear_half.Shape.cut(Part.makeCylinder(1.3,11,V(x,-9,z),V(0,1,0)))
  d.Front_half.Shape=d.Front_half.Shape.cut(Part.makeCylinder(1.7,31,V(x,-.1,z),V(0,1,0))).cut(Part.makeCylinder(3.2,26,V(x,4.8,z),V(0,1,0)))
net=json.loads((P.parent/'wire_netlist.json').read_text())
for w in net:
 n=w['name']; pts=w['points_mm']
 if n=='BAT_plus': pts=pts[:4]+[[-2,0,97],[-2,0,103],[-2,-2.7,103]]
 elif n=='BAT_minus': pts=pts[:4]+[[11,5,99],[-.5,2,99],[-.5,2,106],[-.5,-2.7,106]]
 elif n=='Ground_to_ESP': pts=[[-3,-2.7,113],[-4,-2.7,113],[-4,14,113],[15,14,113],[15,14,151],[16,14,151],[16,2,151],[-17.696,2,151],[-17.696,2,147.4036],[-17.696,-6.1,147.4036]]
 elif n in ('SPI_MOSI','SPI_MISO','SPI_CS'):
  px=pts[-1][0]; lane=pts[3][1]; z=pts[3][2]
  pts=pts[:4]+[[px,lane,z],[px,lane,132.4036],[px,-6.1,132.4036]]
 else: continue
 w['points_mm']=pts
 r=w['diameter_mm']/2; parts=[]
 for a,b in zip(pts,pts[1:]):
  a,b=V(*a),V(*b); delta=b-a
  if delta.Length>1e-7: parts.append(Part.makeCylinder(r,delta.Length,a,delta))
 parts.extend(Part.makeSphere(r,V(*p)) for p in pts[1:-1])
 shape=parts[0].multiFuse(parts[1:])
 assert shape.isValid() and len(shape.Solids)==1,n
 d.getObject(n).Shape=shape; d.getObject(n).Placement=App.Placement()
 w['cut_length_mm']=math.ceil(sum((V(*a)-V(*b)).Length for a,b in zip(pts,pts[1:]))+15)
for n in ('Rear_half','Front_half'):
 s=d.getObject(n).Shape
 assert s.isValid() and len(s.Solids)==1 and s.Volume>70000,n
(P.parent/'wire_netlist.json').write_text(json.dumps(net,indent=2),encoding='utf-8')
d.recompute(); d.save()
result={'file':d.FileName,'rerouted':True,'seam_bores_restored':True}
