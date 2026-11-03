"""Read ZIP/XML/BRep text only, no Linux CAD execution."""
from pathlib import Path
import zipfile,json,hashlib,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
path=root/'3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd'
out=path.parent/'Assembled_View'
visible={'Front_half','Rear_half','Screw_M3_1','Screw_M3_2','Nut_M3_1','Nut_M3_2'}
with zipfile.ZipFile(out/'D36_before_clean_assembled_view.FCStd') as before,zipfile.ZipFile(path) as after:
    files=[n for n in before.namelist() if n.endswith('.brp')]
    flags={}
    for name in files:
        a=before.read(name); b=after.read(name)
        if a==b: continue
        x=a.split(); y=b.split(); assert len(x)==len(y),name
        differences=[(i,j) for i,j in zip(x,y) if i!=j]
        assert all((i,j) in ((b'0111000',b'0101000'),(b'0101000',b'0111000')) for i,j in differences),name
        flags[name]=len(differences)
    old=ET.fromstring(before.read('Document.xml')); new=ET.fromstring(after.read('Document.xml'))
    for node in old.findall('./ObjectData/Object'):
        name=node.attrib['name']; p="./Properties/Property[@name='Placement']/PropertyPlacement"
        a=node.find(p); b=new.find("./ObjectData/Object[@name='%s']"%name).find(p)
        if a is not None: assert a.attrib==b.attrib,name
    gui=ET.fromstring(after.read('GuiDocument.xml'))
    shown=[]
    for node in gui.iter('ViewProvider'):
        prop=node.find("./Properties/Property[@name='Visibility']/Bool")
        if prop is not None and prop.attrib['value']=='true': shown.append(node.attrib['name'])
    assert set(shown)==visible,shown
report={'visible':sorted(visible),'assembled_source_coordinates':True,'geometry_payloads_compared':len(files),'geometry_changed':False,'OCC_checked_flag_changes_only':flags,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'note':'All components, TPU and separated preview links hidden; shell and hardware placements unchanged.'}
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
