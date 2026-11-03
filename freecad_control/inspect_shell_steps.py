import FreeCAD as App
import FreeCADGui as Gui
from pathlib import Path
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
root=Path(doc.FileName).parent
Gui.activeDocument().activeView().saveImage(str(root/'current_steps_view.png'),1400,1100,'White')
data={}
for name in ('Front_half','Rear_half'):
    faces=[]
    for i,f in enumerate(doc.getObject(name).Shape.Faces):
        if 'Plane' not in str(type(f.Surface)):continue
        b=f.optimalBoundingBox(False,False)
        faces.append({'face':i+1,'area':round(f.Area,4),'normal':[round(v,4) for v in f.normalAt(0,0)],'bounds':[round(v,4) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]})
    data[name]=faces
result={'selection':[{'object':s.ObjectName,'sub':s.SubElementNames} for s in Gui.Selection.getSelectionEx()],'faces':data,'image':str(root/'current_steps_view.png')}
