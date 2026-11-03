from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
import json,hashlib
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'))
for o in doc.Objects:o.Visibility=True
view=Gui.activeDocument().activeView();view.setCameraType('Orthographic')
node=view.getCameraNode()
rotation=App.Rotation(App.Vector(180,-150,0),App.Vector(0,0,1),App.Vector(150,180,77),'ZXY')
node.orientation.setValue(coin.SbRotation(*rotation.Q))
direction=App.Vector(150,180,77);direction.normalize()
position=App.Vector(0,0,68)+direction*250
node.position.setValue(*position);node.height.setValue(160)
Gui.Selection.clearSelection();doc.save()
out=Path(doc.FileName).parent/'Lower_Screw'
report=json.loads((out/'validation.json').read_text(encoding='utf-8'))
report['integral_boss_envelope_XYZ_mm']=[11.8,18,-18,18,5.3,12.7]
report['sha256']=hashlib.sha256(Path(doc.FileName).read_bytes()).hexdigest()
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result={'sha256':report['sha256'],'view':'Closed assembly; new lower M2 joint visible from front/right'}
