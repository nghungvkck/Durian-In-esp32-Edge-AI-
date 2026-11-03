from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part, zipfile, json, hashlib
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Recessed_Fasteners'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
backup=out/'D36_before_recessed_fasteners.FCStd'
refs=[]
with zipfile.ZipFile(backup) as archive:
    xml=ET.fromstring(archive.read('Document.xml'))
    for node in xml.findall('./ObjectData/Object'):
        name=node.attrib['name']
        if name in ('Front_half','Rear_half') or name.startswith('Preview_'): continue
        prop=node.find("./Properties/Property[@name='Shape']/Part")
        if prop is None: continue
        tmp=out/'reference_verify.brp'; tmp.write_bytes(archive.read(prop.attrib['file']))
        s=Part.Shape(); s.read(str(tmp)); tmp.unlink()
        o=doc.getObject(name)
        p=node.find("./Properties/Property[@name='Placement']/PropertyPlacement").attrib
        pl=App.Placement(App.Vector(*[float(p[k]) for k in ('Px','Py','Pz')]),App.Rotation(*[float(p[k]) for k in ('Q0','Q1','Q2','Q3')]))
        assert (o.Placement.Base-pl.Base).Length<1e-9 and o.Placement.Rotation.isSame(pl.Rotation,1e-9), name+' placement'
        assert abs(s.Volume-o.Shape.Volume)<1e-7, name+' volume'
        assert s.cut(o.Shape).Volume+o.Shape.cut(s).Volume<1e-6, name+' geometry'
        refs.append(name)
assert len(refs)==37
hardware=[f'{kind}_M3_{i}' for i in (1,2) for kind in ('Screw','Nut')]
for name in hardware:
    s=doc.getObject(name).Shape
    assert s.isValid() and len(s.Solids)==1
    for other in ('Front_half','Rear_half',*refs):
        if other.endswith('_Print'): continue
        assert s.common(doc.getObject(other).Shape).Volume<1e-6, name+' clash '+other
for i in (1,2):
    assert doc.getObject(f'Screw_M3_{i}').Shape.common(doc.getObject(f'Nut_M3_{i}').Shape).Volume<1e-6
for name in ('Front_half','Rear_half'):
    s=doc.getObject(name).Shape
    assert s.isValid() and len(s.Solids)==1
    b=s.optimalBoundingBox(False,False)
    assert abs(b.XLength-36)<1e-6 and abs(b.ZLength-136)<1e-6
assert doc.Front_half.Shape.common(doc.Rear_half.Shape).Volume<1e-6
view=Gui.activeDocument().activeView(); view.viewAxonometric(); view.fitAll(); Gui.Selection.clearSelection()
doc.recompute(); doc.save()
checked={}
with zipfile.ZipFile(path) as archive:
    xml=ET.fromstring(archive.read('Document.xml'))
    for node in xml.findall('./ObjectData/Object'):
        name=node.attrib['name']
        if name not in ('Front_half','Rear_half',*hardware): continue
        prop=node.find("./Properties/Property[@name='Shape']/Part")
        tmp=out/'saved_verify.brp'; tmp.write_bytes(archive.read(prop.attrib['file']))
        s=Part.Shape(); s.read(str(tmp)); tmp.unlink()
        expected=doc.getObject(name).Shape
        assert s.isValid() and len(s.Solids)==1
        assert s.cut(expected).Volume+expected.cut(s).Volume<1e-6
        checked[name]={'valid':True,'solids':len(s.Solids),'volume_mm3':s.Volume}
assert len(checked)==6
report={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup':str(backup),'hole_diameter_mm':4,'centers_XZ_mm':[[0,111],[0,131]],'screw':'2 x M3 x 30, nominal head D5.5 H3, socket AF2.5; simplified, no helical thread','head_seat_Y_mm':13,'head_top_Y_mm':16,'head_pocket_diameter_mm':6.2,'nut':'2 x M3 AF5.5 H2.4; simplified, no helical thread','nut_pocket_AF_mm':5.9,'nut_seat_Y_mm':-14.1,'nut_outer_Y_mm':-16.5,'screw_tip_Y_mm':-17,'unchanged_reference_count':len(refs),'shell_hardware_component_volume_interference_mm3':0,'serialized_BRep':checked,'limits':'Nominal model, real hardware dimensions/tolerances, printed fit and clamping untested. Nut pocket prevents rotation, not falling out before assembly.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
