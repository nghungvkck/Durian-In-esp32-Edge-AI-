from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import json,hashlib
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
out=Path(doc.FileName).parent/'Simplified_Holder_Steps'
report=json.loads((out/'validation.json').read_text(encoding='utf-8'))
for name in ('Front_half','Rear_half'):
    obj=doc.getObject(name)
    assert abs(obj.Shape.Volume-report['saved_shells'][name]['volume_mm3'])<1e-6
    obj.ViewObject.DisplayMode='Shaded'
Gui.Selection.clearSelection();doc.save()
report['display']='Shaded shells; removeSplitter was rejected on both shells because its result failed validity. Original valid fused shapes retained.'
report['sha256']=hashlib.sha256(Path(doc.FileName).read_bytes()).hexdigest()
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result={'saved':True,'sha256':report['sha256'],'display':report['display']}
