"""Cut centered 20 x 3 mm axial slot; preserve the switch-end floor."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
SOURCE=ROOT/'3D/Enclosure_Three_Seam_Screws_D50/Enclosure_Three_Seam_Screws_D50.FCStd'
OUT=ROOT/'3D/Enclosure_Center_Slot_D50'
src=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==SOURCE)
assert not OUT.exists(), 'Output already exists; inspect before repeating'
tool=Part.makeBox(20,3,199,App.Vector(-10,-1.5,3))
floor=Part.makeBox(60,60,3,App.Vector(-30,-30,0))
new_shapes={}
checks={}
for name in ('Rear_half','Front_half'):
    original=src.getObject(name).Shape
    changed=original.cut(tool)
    assert changed.isValid() and len(changed.Solids)==1, name
    assert changed.Volume>70000 and abs(changed.BoundBox.ZLength-201)<.001
    assert original.common(floor).cut(changed).Volume<.001, 'Bottom floor changed'
    assert changed.common(tool).Volume<.001, 'Slot obstructed'
    checks[name]={'before_mm3':original.Volume,'after_mm3':changed.Volume,'removed_mm3':original.Volume-changed.Volume,'bottom_floor_unchanged':True}
    new_shapes[name]=changed
doc=App.newDocument('Enclosure_Center_Slot_D50')
for obj in src.Objects:
    doc.copyObject(obj,False)
for name,shape in new_shapes.items():
    doc.getObject(name).Shape=shape
    obj=doc.getObject(name)
    obj.addProperty('App::PropertyString','CenterSlot','Design')
    obj.CenterSlot='20 mm X x 3 mm Y, centered X0/Y0; axial cut Z3..201; switch floor Z0..3 preserved'
doc.recompute()
assert doc.SW1.Shape.cut(src.SW1.Shape).Volume<.001
App.setActiveDocument(doc.Name)
for obj in doc.Objects:
    if obj.TypeId=='Part::Feature':
        obj.Visibility=obj.Name not in ('Charge_plug_envelope','Code_plug_envelope','Mic_Edge_Screw_L','Mic_Edge_Screw_R','Key_Screw_55','Key_Screw_85')
Gui.Selection.clearSelection()
v=Gui.activeDocument().activeView()
v.viewTop(); v.fitAll()
OUT.mkdir()
v.saveImage(str(OUT/'center_slot_top.png'),1200,1000,'White')
doc.saveAs(str(OUT/'Enclosure_Center_Slot_D50.FCStd'))
(OUT/'slot_change.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
result={'file':doc.FileName,'slot_mm':[20,3],'center_xy_mm':[0,0],'cut_z_mm':[3,201],'checks':checks}
