import FreeCAD as App
import Part
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
items=[]
for o in doc.Objects:
    if o.Name.endswith('_half'):continue
    b=o.Shape.optimalBoundingBox(False,False)
    items.append({'name':o.Name,'bounds':[round(v,4) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]})
result={'components':items}
