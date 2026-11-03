from pathlib import Path
import FreeCADGui as Gui
path=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\3D\Enclosure_Compact_Layout_D36\Printed_Retention_35x25x6\Reinforced_Frame\reinforced_frame.png')
Gui.activeDocument().activeView().saveImage(str(path),1300,1000,'White')
result={'image':str(path)}
