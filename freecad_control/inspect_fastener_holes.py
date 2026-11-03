from pathlib import Path
import FreeCAD as App
doc = next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
data = {}
for name in ('Front_half','Rear_half'):
    obj = doc.getObject(name)
    faces = []
    for i,f in enumerate(obj.Shape.Faces):
        s=f.Surface
        if 'Cylinder' in str(type(s)):
            b=f.BoundBox
            faces.append({'face':i+1,'radius':s.Radius,'center':list(s.Center),'axis':list(s.Axis),'bounds':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
    data[name]=faces
result={'file':doc.FileName,'cylinders':data,'objects':[{'name':o.Name,'visible':o.Visibility,'placement':str(o.Placement)} for o in doc.Objects]}
