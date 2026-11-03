"""Open/show the current D36 assembly without changing geometry or saving."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
try:
    from PySide import QtWidgets
except ImportError:
    from PySide import QtGui as QtWidgets

project_root = Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
assembly_path = project_root / '3D' / 'Enclosure_Compact_Layout_D36' / 'Printed_Retention_35x25x6' / 'D36_Printed_Retention_35x25x6.FCStd'
assert assembly_path.is_file(), 'Current D36 assembly is missing: ' + str(assembly_path)
assembly = next((doc for doc in App.listDocuments().values()
                 if doc.FileName and str(Path(doc.FileName)).casefold() == str(assembly_path).casefold()), None)
if assembly is None:
    assembly = App.openDocument(str(assembly_path))

shells = {}
for name in ('Front_half', 'Rear_half'):
    obj = assembly.getObject(name)
    assert obj is not None, 'Missing source shell: ' + name
    shape = obj.Shape
    bounds = shape.optimalBoundingBox(False, False)
    assert shape.isValid() and len(shape.Solids) == 1, 'Invalid source shell: ' + name
    assert abs(bounds.XLength - 36) < .01 and abs(bounds.ZLength - 146) < .01, 'Unexpected D36 dimensions: ' + name
    shells[name] = {'valid': True, 'solids': 1, 'volume_mm3': round(shape.Volume, 6)}

App.setActiveDocument(assembly.Name)
visible_names = ('Front_half', 'Rear_half', 'Screw_M3_1', 'Screw_M3_2', 'Nut_M3_1', 'Nut_M3_2', 'Screw_M3_Lower', 'Nut_M3_Lower')
assert all(assembly.getObject(name) is not None for name in visible_names), 'Assembled shells or fasteners are missing'
visible_names += ('Battery','MicroSD','IP5306','ESP32_C3','SW1','SW1_Terminals',
                  'Key_PCB','Key_Mount_Rings','Key_Pads','Mic_PCB','Mic_ICS43434','Mic_Pads','Mic_Passives')
visible_names += tuple('Key_%s_%s' % (part,i) for i in (1,2,3) for part in ('Case','Body','Stem','Leads'))
for obj in assembly.Objects:
    if hasattr(obj, 'ViewObject'):
        obj.Visibility = obj.Name in visible_names
view = Gui.activeDocument().activeView()
view.viewFront()
view.fitAll()
Gui.Selection.clearSelection()
mdi = Gui.getMainWindow().findChild(QtWidgets.QMdiArea)
if mdi:
    for window in mdi.subWindowList():
        if assembly_path.stem in window.windowTitle() or assembly.Label in window.windowTitle():
            mdi.setActiveSubWindow(window)
            window.showMaximized()
            break

result = {
    'active_document': assembly.Name,
    'file': str(assembly_path),
    'shells': shells,
    'dimensions_mm': [36, 146],
    'view': 'Closed assembled shells, screws/nuts and selected electronics at installed coordinates. No TPU or separated previews.',
    'status': 'Selected electronics restored; physical joint and print validation unfinished. No D36 STL.',
    'geometry_changed': False,
    'saved': False,
}
