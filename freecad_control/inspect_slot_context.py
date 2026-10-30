import FreeCAD as App
import FreeCADGui as Gui
d=App.ActiveDocument
def bounds(s):
    b=s.BoundBox
    return [b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]
result={'active':d.Name,'file':d.FileName,'camera':list(Gui.activeDocument().activeView().getCameraOrientation().Q),'selection':[(s.Object.Name,s.SubElementNames) for s in Gui.Selection.getSelectionEx()], 'objects':{n:{'bounds':bounds(d.getObject(n).Shape),'volume':d.getObject(n).Shape.Volume} for n in ('Rear_half','Front_half','SW1','Battery')},'modified':d.UndoCount}
