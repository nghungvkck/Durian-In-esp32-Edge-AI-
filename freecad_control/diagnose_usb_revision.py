"""Run the existing full checks on the draft revision without exporting."""
from pathlib import Path
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
p=ROOT/'freecad_control/validate_latest.py'
code=p.read_text(encoding='utf-8').replace('Enclosure_Center_Slot_D50','Enclosure_USB_Near_Wall_D50')
ns={'__name__':'__usb_diagnostic__','check_stl':False}
try:
    exec(compile(code,str(p),'exec'),ns)
    result=ns['result']
except AssertionError as error:
    result={'assertion':str(error),'report':ns.get('report',{})}
