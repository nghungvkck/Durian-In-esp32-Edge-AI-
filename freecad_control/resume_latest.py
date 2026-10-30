"""Open the accepted CAD assembly through the bridge, without old session globals."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part
try:
    from PySide import QtWidgets
except ImportError:
    from PySide import QtGui as QtWidgets

project_root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
assembly_path=project_root/'3D'/'Enclosure_USB_Near_Wall_D50'/'Enclosure_USB_Near_Wall_D50.FCStd'
assert assembly_path.is_file(), 'Accepted assembly is missing: '+str(assembly_path)
assembly=None
for candidate in App.listDocuments().values():
    if candidate.FileName and str(Path(candidate.FileName)).casefold()==str(assembly_path).casefold():
        assembly=candidate
        break
if assembly is None:
    assembly=App.openDocument(str(assembly_path))
App.setActiveDocument(assembly.Name)
for name in ('Rear_half','Front_half','Mic_PCB','ESP32_C3'):
    assert assembly.getObject(name) is not None, 'Unexpected document: missing '+name
halves={}
for name in ('Rear_half','Front_half'):
    shape=assembly.getObject(name).Shape
    assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>40000, 'Check full shell geometry: '+name
    assert abs(shape.BoundBox.XLength-50)<.01 and abs(shape.BoundBox.ZLength-201)<.01, 'Unexpected shell dimensions: '+name
    halves[name]={'valid':True,'solids':1,'volume_mm3':round(shape.Volume,3)}
for obj in assembly.Objects:
    if obj.TypeId=='Part::Feature':
        obj.Visibility=obj.Name not in ('Front_half','Charge_plug_envelope','Code_plug_envelope','Mic_Edge_Screw_L','Mic_Edge_Screw_R','Key_Screw_55','Key_Screw_85')
assembly.Rear_half.ViewObject.Transparency=0
assembly.Front_half.ViewObject.Transparency=0
normal=App.Vector(.65,1,.12); normal.normalize()
right=App.Vector(0,0,1).cross(normal); right.normalize()
up=normal.cross(right)
view=Gui.activeDocument().activeView()
view.setCameraOrientation(App.Rotation(right,up,normal,'ZXY').Q)
view.fitAll()
Gui.Selection.clearSelection()
mdi=Gui.getMainWindow().findChild(QtWidgets.QMdiArea)
if mdi:
    for window in mdi.subWindowList():
        if Path(assembly.FileName).stem in window.windowTitle() or assembly.Label in window.windowTitle():
            mdi.setActiveSubWindow(window)
            window.showMaximized()
            break
assembly.recompute()
mic=assembly.Mic_PCB.Shape.BoundBox
esp=assembly.ESP32_C3.Shape.BoundBox
assert mic.ZMin>esp.ZMax, 'Microphone is not entirely above ESP32'
assert mic.ZLength>12 and mic.YLength<2, 'Microphone is not upright in XZ'
sd=assembly.MicroSD.Shape.BoundBox
assert abs(sd.XLength-24)<.01 and abs(sd.ZLength-44.748333193)<.01, 'SD is not in the vertical layout'
keys=assembly.getObject('Key_PCB')
assert keys is not None and abs(keys.Shape.BoundBox.ZLength-36)<.01, 'Three-button module missing'
for board in ('IP5306','ESP32_C3'):
    assert abs(assembly.getObject(board).Shape.BoundBox.XMin+23)<.001, 'USB port is not at the accepted near-wall position: '+board
assert abs(keys.Shape.BoundBox.ZMin-130)<.01 and abs(keys.Shape.BoundBox.ZMax-166)<.01, 'Buttons are not near the solid top'
for z in (176,196):
    probe=Part.makeCylinder(1.9,52,App.Vector(0,-26,z),App.Vector(0,1,0))
    assert all(probe.common(assembly.getObject(n).Shape).Volume<.001 for n in ('Rear_half','Front_half')), 'Top mounting bore blocked'
result={'active_document':assembly.Name,'file':str(assembly_path),
        'shells':halves,'microphone_upright':True,
        'microphone_pcb_z':[mic.ZMin,mic.ZMax],
        'microphone_gap_above_esp_mm':round(mic.ZMin-esp.ZMax,3),
        'sd_vertical':True,'dimensions_mm':[50,201],'solid_extension_z_mm':[171,201],
        'three_button_module':True,'button_pcb_z':[130,166],'gap_to_solid_mm':2,
        'top_mount_holes':{'diameter_mm':4,'pitch_mm':20,'axis':'Y','center_x_mm':0,'center_z_mm':[176,196]},
        'view':'Front hidden, whole rear visible. No geometry changed or file saved.'}
