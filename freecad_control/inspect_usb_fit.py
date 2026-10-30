from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part, json
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
P=ROOT/'3D/Enclosure_Center_Slot_D50/Enclosure_Center_Slot_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==P)
def bb(s):
 b=s.BoundBox
 return [round(v,4) for v in (b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax)]
data={}
for name in ('IP5306','ESP32_C3','Charge_plug_envelope','Code_plug_envelope','Boost_to_switch','Switch_to_ESP','Ground_to_ESP','BAT_plus','BAT_minus'):
 o=d.getObject(name); s=o.Shape
 data[name]={'bounds':bb(s),'solids':[{'volume':round(p.Volume,3),'bounds':bb(p)} for p in s.Solids], 'placement':str(o.Placement),'properties':{k:str(getattr(o,k)) for k in o.PropertiesList if k not in ('Shape','Placement') and o.getGroupOfProperty(k)=='Design'}}
 if name in ('IP5306','ESP32_C3'):
  data[name]['shells']=[{'faces':len(p.Faces),'bounds':bb(p)} for p in s.Shells][:50]
(ROOT/'freecad_control/usb_before_inspection.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
result=data
