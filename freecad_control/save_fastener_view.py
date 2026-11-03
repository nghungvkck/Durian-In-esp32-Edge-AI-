from pathlib import Path
import FreeCADGui as Gui
out=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\3D\Enclosure_Compact_Layout_D36\Printed_Retention_35x25x6\Recessed_Fasteners\fasteners.png')
Gui.activeDocument().activeView().saveImage(str(out),1400,1100,'White')
result={'image':str(out)}
