from pathlib import Path
import FreeCADGui as Gui
p=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\3D\Enclosure_Compact_Layout_D36\Printed_Retention_35x25x6\Assembled_View\assembled.png')
Gui.activeDocument().activeView().saveImage(str(p),1100,1100,'White')
result={'image':str(p)}
