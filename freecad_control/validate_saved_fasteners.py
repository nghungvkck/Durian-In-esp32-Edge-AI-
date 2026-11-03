from pathlib import Path
import FreeCAD as App
import Part, zipfile, json, hashlib
import xml.etree.ElementTree as ET
root=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Recessed_Fasteners'
doc=next(d for d in App.listDocuments().values() if d.FileName and str(Path(d.FileName)).casefold()==str(path).casefold())
hardware=[f'{kind}_M3_{i}' for i in (1,2) for kind in ('Screw','Nut')]
checked={}; refs=[]; numeric_roundoff={}
with zipfile.ZipFile(out/'D36_before_recessed_fasteners.FCStd') as before, zipfile.ZipFile(path) as after:
    oldxml=ET.fromstring(before.read('Document.xml')); newxml=ET.fromstring(after.read('Document.xml'))
    for oldnode in oldxml.findall('./ObjectData/Object'):
        name=oldnode.attrib['name']
        if name in ('Front_half','Rear_half') or name.startswith('Preview_'): continue
        prop=oldnode.find("./Properties/Property[@name='Shape']/Part")
        if prop is None: continue
        newnode=newxml.find("./ObjectData/Object[@name='%s']"%name)
        newprop=newnode.find("./Properties/Property[@name='Shape']/Part")
        olddata=before.read(prop.attrib['file']); newdata=after.read(newprop.attrib['file'])
        if olddata!=newdata:
            a=olddata.decode('ascii').split(); b=newdata.decode('ascii').split()
            assert len(a)==len(b), name+' topology changed'
            largest=0.; count=0; checked_flags=0
            for x,y in zip(a,b):
                if x==y: continue
                if (x,y) in (('0101000','0111000'),('0111000','0101000')):
                    checked_flags+=1
                    continue
                delta=abs(float(x)-float(y))
                assert delta<1e-12, name+' BRep token changed'
                largest=max(largest,delta); count+=1
            numeric_roundoff[name]={'differing_numeric_tokens':count,'maximum_absolute_delta':largest,'OCC_checked_flags_changed':checked_flags}
        assert oldnode.find("./Properties/Property[@name='Placement']/PropertyPlacement").attrib==newnode.find("./Properties/Property[@name='Placement']/PropertyPlacement").attrib, name+' placement changed'
        refs.append(name)
    for name in ('Front_half','Rear_half',*hardware):
        node=newxml.find("./ObjectData/Object[@name='%s']"%name)
        prop=node.find("./Properties/Property[@name='Shape']/Part")
        tmp=out/'saved_verify.brp'; tmp.write_bytes(after.read(prop.attrib['file']))
        s=Part.Shape(); s.read(str(tmp)); tmp.unlink()
        expected=doc.getObject(name).Shape
        assert s.isValid() and len(s.Solids)==1
        assert abs(s.Volume-expected.Volume)<1e-6
        b=s.optimalBoundingBox(False,False); e=expected.optimalBoundingBox(False,False)
        assert all(abs(a-c)<1e-5 for a,c in zip((b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax),(e.XMin,e.YMin,e.ZMin,e.XMax,e.YMax,e.ZMax))), name+' bounds'
        if name.endswith('_half'): assert abs(b.XLength-36)<.001 and abs(b.ZLength-136)<.001
        checked[name]={'valid':True,'solids':1,'volume_mm3':s.Volume,'bbox_mm':[b.XLength,b.YLength,b.ZLength]}
assert len(refs)==37
report={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':len(doc.Objects),'hole_diameter_mm':4,'centers_XZ_mm':[[0,111],[0,131]],'screw':'2 x M3 x 30, head D5.5 H3, socket AF2.5, simplified no helical thread','head_seat_Y_mm':13,'head_top_Y_mm':16,'head_pocket_diameter_mm':6.2,'nut':'2 x M3 AF5.5 H2.4, simplified no helical thread','nut_pocket_AF_mm':5.9,'nut_seat_Y_mm':-14.1,'nut_outer_Y_mm':-16.5,'tip_Y_mm':-17,'unchanged_reference_payload_and_placement_count':len(refs),'reference_serialization_roundoff':numeric_roundoff,'serialized_BRep':checked,'pre_save_validation':'add_recessed_fasteners.py passed shell valid/one solid/envelope, shell-shell and hardware-shell/component volume checks and unchanged bore segment checks before saving; basic BoundBox comparison after save was unsuitable, replaced here with optimalBoundingBox(False,False).','limits':'Real hardware dimensions, print tolerances, insertion and clamping strength untested. Nut pocket resists rotation, not falling out before screw engagement.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
result=report
