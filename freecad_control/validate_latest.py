"""Read-only validation of the accepted CAD assembly; no files written."""
from pathlib import Path
import math
import FreeCAD as App
import Part, Mesh
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
ASSEMBLY=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
doc=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==ASSEMBLY),None)
assert doc is not None, 'Run resume_latest.py first'
V=App.Vector
shapes={o.Name:o.Shape for o in doc.Objects if o.TypeId=='Part::Feature'}
report={'file':str(ASSEMBLY),'dimensions_mm':[50,201],'printed_parts':{},'intersections':[],'tolerance_mm3':.02}
check_stl=globals().get('check_stl',True)
report['stl_checked']=check_stl
shells=['Rear_half','Front_half']
for name in shells:
    s=shapes[name]; b=s.BoundBox
    assert s.isValid() and len(s.Solids)==1 and s.Volume>70000, name
    assert abs(b.XLength-50)<.001 and abs(b.ZLength-201)<.001, name
    report['printed_parts'][name]={'valid':True,'solids':1,'volume_mm3':s.Volume}
    if check_stl:
        mesh=Mesh.Mesh(str(ASSEMBLY.parent/'STL'/(name+'.stl')))
        assert mesh.isSolid(), 'Open STL: '+name
        report['printed_parts'][name].update({'stl_closed':True,'stl_facets':mesh.CountFacets})
sewn=shapes['IP5306'].copy(); sewn.sewShape()
shapes['IP5306']=Part.makeCompound([Part.makeSolid(s) for s in sewn.Shells])
skip={'Mic_Edge_Screw_L','Mic_Edge_Screw_R','Key_Screw_55','Key_Screw_85'}
refs=[n for n in shapes if n not in skip and n not in shells]
wires=['BAT_plus','BAT_minus','Boost_to_switch','Switch_to_ESP','Ground_to_ESP','SD_5V','SD_GND','SPI_SCK','SPI_MOSI','SPI_MISO','SPI_CS']
electronics=['Battery','MicroSD','IP5306','ESP32_C3','SW1','Mic_PCB','Mic_ICS43434','Mic_Pads','Mic_Passives','Mic_Acoustic_Gasket']
keys=[n for n in shapes if n.startswith('Key_') and 'Screw' not in n]
assert all(shapes[n].isValid() for n in keys)
pairs=[('Rear_half','Front_half')]+[(a,b) for a in shells for b in refs]
pairs += [(a,b) for a in wires for b in electronics]
pairs += [(a,b) for i,a in enumerate(electronics) for b in electronics[i+1:]]
pairs += [(a,b) for a in keys for b in electronics+wires+['Charge_plug_envelope','Code_plug_envelope']]
for i,a in enumerate(wires):
    for b in wires[i+1:]:
        if {a,b}<={'Switch_to_ESP','SD_5V'} or {a,b}<={'Ground_to_ESP','SD_GND'}: continue
        pairs.append((a,b))
for a,b in pairs:
    if not shapes[a].BoundBox.intersect(shapes[b].BoundBox): continue
    volume=shapes[a].common(shapes[b]).Volume
    if volume>.02: report['intersections'].append({'a':a,'b':b,'volume_mm3':volume})
holes=[(0,159,.6)]+[(1.2*math.cos(math.radians(a)),159+1.2*math.sin(math.radians(a)),.45) for a in range(0,360,60)]
report['acoustic_paths_clear']=sum(Part.makeCylinder(r*.9,5.7,V(x,-26,z),V(0,1,0)).common(shapes['Rear_half']).Volume<.001 for x,z,r in holes)
report['button_access_clear']=[Part.makeCylinder(2.1,3.1,V(0,22.9,z),V(0,1,0)).common(shapes['Front_half']).Volume<.001 for z in (140,148,156)]
filled=shapes['Rear_half'].fuse(shapes['Front_half'])
cutters=Part.makeCompound([Part.makeCylinder(2,60,V(0,-30,z),V(0,1,0)) for z in (176,196)])
slot=Part.makeBox(20,3,199,V(-10,-1.5,3))
expected=Part.makeCylinder(25,30,V(0,0,171)).cut(cutters).cut(slot)
missing=expected.cut(filled).Volume; remaining=filled.common(cutters).Volume
assert missing<.001 and remaining<.001, 'Cap or mounting holes differ from accepted geometry'
report['solid_extension']={'z_mm':[171,201],'missing_unexpected_mm3':missing}
assert filled.common(slot).Volume<.001, 'Centered rectangular slot blocked'
floor_probe=Part.makeBox(19.8,2.8,2.8,V(-9.9,-1.4,.1))
assert abs(filled.common(floor_probe).Volume-floor_probe.Volume)<.001, 'Floor below slot breached'
report['center_slot']={'size_xy_mm':[20,3],'center_xy_mm':[0,0],'cut_z_mm':[3,201],'switch_end_floor_mm':3,'floor_intact':True}
report['mount_holes']={'diameter_mm':4,'pitch_mm':20,'axis':[0,1,0],'centers_mm':[[0,0,176],[0,0,196]],'residual_material_in_bores_mm3':remaining}
sd=shapes['MicroSD'].BoundBox; keys=shapes['Key_PCB'].BoundBox
assert abs(sd.XLength-24)<.01 and abs(sd.ZLength-44.748333193)<.01
assert abs(keys.ZMin-130)<.01 and abs(keys.ZMax-166)<.01
assert shapes['Mic_PCB'].BoundBox.ZMin>shapes['ESP32_C3'].BoundBox.ZMax
report['button_pcb_z_mm']=[keys.ZMin,keys.ZMax]
report['usb_ports']={}
for board,plug,shift in [('IP5306','Charge_plug_envelope',-10),('ESP32_C3','Code_plug_envelope',-11)]:
    mouth=shapes[board].BoundBox.XMin
    assert abs(mouth+23)<.001, 'USB mouth must be near side wall: '+board
    clearance={n:shapes[n].common(shapes[plug]).Volume for n in shells}
    assert max(clearance.values())<.001, 'Cable overmold blocked: '+board
    report['usb_ports'][board]={'mouth_x_mm':mouth,'shift_x_mm':shift,'recess_at_centerline_mm':math.sqrt(25**2-5.5**2)-abs(mouth),'plug_shell_overlap_mm3':clearance}
for x in (-21,21):
    for z in (43,127):
        probe=Part.makeCylinder(.8,1,V(x,10,z),V(0,1,0))
        assert abs(probe.common(shapes['Front_half']).Volume-probe.Volume)<.001, 'Removed seam screw hole remains'
    for z in (14,97,166):
        probe=Part.makeCylinder(1.1,21,V(x,-8.9,z),V(0,1,0))
        assert all(probe.common(shapes[n]).Volume<.001 for n in shells), 'Remaining seam screw blocked'
report['seam_screws']={'per_side':3,'total':6,'x_mm':[-21,21],'kept_z_mm':[14,97,166],'removed_z_mm':[43,127]}
report['notes']=['Read-only check; no files written.','Reference hardware dimensions remain provisional; button/I2S wires not added.','Intentional screw/fixture contacts and internal button module joints excluded.','No physical print, assembly or load test performed.']
report['passed']=not report['intersections'] and report['acoustic_paths_clear']==7 and all(report['button_access_clear'])
assert report['passed'], str(report)
result=report
