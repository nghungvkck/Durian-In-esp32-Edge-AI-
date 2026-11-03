"""Persist clean assembled view; retain hidden reference geometry for future edits."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin
import shutil,zipfile,hashlib,json
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Assembled_View'; out.mkdir(exist_ok=True)
backup=out/'D36_before_clean_assembled_view.FCStd'
assert not backup.exists(), 'View change backup already exists; inspect before rerun'
shutil.copy2(path,backup)
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
App.setActiveDocument(doc.Name)
visible=('Front_half','Rear_half','Screw_M3_1','Screw_M3_2','Nut_M3_1','Nut_M3_2')
for obj in doc.Objects:
    obj.Visibility=obj.Name in visible
    if obj.Name in visible:
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
        obj.ViewObject.DisplayMode='Flat Lines' if obj.Name.startswith(('Screw','Nut')) else 'Flat Lines'
        obj.ViewObject.Transparency=0
        assert obj.Placement.Base.Length<1e-8, obj.Name+' is displaced'
view=Gui.activeDocument().activeView()
view.setCameraType('Orthographic')
node=view.getCameraNode()
rotation=App.Rotation(App.Vector(180,-150,0),App.Vector(0,0,1),App.Vector(150,180,77),'ZXY')
node.orientation.setValue(coin.SbRotation(*rotation.Q))
direction=App.Vector(150,180,77); direction.normalize()
position=App.Vector(0,0,68)+direction*250
node.position.setValue(*position)
node.height.setValue(160)
Gui.Selection.clearSelection(); doc.recompute(); doc.save()
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(path) as after:
    files=[n for n in before.namelist() if n.lower().endswith(('.brp','.brep'))]
    assert files
    assert all(before.read(n)==after.read(n) for n in files), 'Geometry payload changed during view-only edit'
report={'visible':list(visible),'assembled_source_coordinates':True,'geometry_payloads_unchanged':len(files),'objects':len(doc.Objects),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup),'note':'All boards, small R/C, TPU and separated preview links hidden. No placement or geometry changes. Two screws span both shells in assembled coordinates.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
