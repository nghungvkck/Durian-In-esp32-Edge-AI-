from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import json
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
out=Path(doc.FileName).parent
data={}
for name in ('Front_half','Rear_half'):
    faces=[]
    for i,f in enumerate(doc.getObject(name).Shape.Faces):
        b=f.optimalBoundingBox(False,False)
        if b.ZMin<24 or b.ZMax>65 or b.XLength<18:continue
        faces.append({'face':i+1,'area':f.Area,'bounds':[round(v,6) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]})
    data[name]=faces
Gui.activeDocument().activeView().saveImage(str(out/'frame_bars_before.png'),1300,1000,'White')
result={'faces':data,'visible':[o.Name for o in doc.Objects if o.Visibility],'selection':[{'name':s.ObjectName,'sub':s.SubElementNames} for s in Gui.Selection.getSelectionEx()]}
