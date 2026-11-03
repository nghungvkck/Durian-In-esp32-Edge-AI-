"""Export only saved, reinforced source shells; leave GUI/CAD unchanged."""
from pathlib import Path
import FreeCAD as App
import Part,Mesh,MeshPart,json,zipfile,hashlib
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Print_2026-11-03';out.mkdir(exist_ok=True)
source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
assert source_hash=='30ffa569b3b1985c07a908fed7001bee70d0980014a19a7e67fb60a15af345c7','Saved CAD changed; inspect before export'
expected={'Front_half':29340.783388500888,'Rear_half':30828.065378586965}
report={'source':str(path),'source_sha256':source_hash,'units':'mm','linear_deflection_mm':.05,'angular_deflection_rad':.15,'relative':False,'exports':{},'note':'Only two reinforced shell solids, no metal screws, nuts or electronics. Assembly coordinates retained. No slicer/G-code or physical print validation.'}
with zipfile.ZipFile(path) as archive:
    xml=ET.fromstring(archive.read('Document.xml'))
    for name,volume in expected.items():
        target=out/('D36_'+name+'_2026-11-03.stl')
        assert not target.exists(),'Export already exists; do not overwrite '+str(target)
        node=xml.find("./ObjectData/Object[@name='%s']"%name)
        tmp=out/(name+'_source.brp')
        tmp.write_bytes(archive.read(node.find("./Properties/Property[@name='Shape']/Part").attrib['file']))
        s=Part.Shape();s.read(str(tmp));tmp.unlink()
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-volume)<1e-6
        b=s.optimalBoundingBox(False,False)
        assert abs(b.XLength-36)<.001 and abs(b.ZLength-146)<.001
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
        assert mesh.CountFacets>0 and mesh.isSolid(),name+' generated mesh not closed solid'
        mesh.write(str(target))
        reread=Mesh.Mesh(str(target))
        assert reread.CountFacets==mesh.CountFacets and reread.isSolid(),name+' STL readback failed'
        mb=reread.BoundBox
        assert abs(mb.XLength-36)<.11 and abs(mb.ZLength-146)<.01
        mv=abs(reread.Volume)
        assert abs(mv-volume)/volume<.005,name+' volume approximation >0.5%'
        report['exports'][name]={'file':str(target),'facets':reread.CountFacets,'points':reread.CountPoints,'closed_solid':reread.isSolid(),'solid_volume_mm3':volume,'mesh_volume_mm3':mv,'bounds_mm':[mb.XLength,mb.YLength,mb.ZLength],'size_bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
assert hashlib.sha256(path.read_bytes()).hexdigest()==source_hash,'CAD file changed during export'
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
