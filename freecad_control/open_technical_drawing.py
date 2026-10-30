"""Package dimensioned vector sheets as a separate FreeCAD TechDraw document.

SVG annotations and projections are a static snapshot of this CAD revision.
Do not imply associative dimensions; regenerate after changing geometry.
"""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
P=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
OUT=P.parent/'Technical_Drawing'
target=OUT/'Ban_ve_ky_thuat_Vo_tru_D50.FCStd'
src=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==P)
draw=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==target),None)
if draw is None:
    draw=App.newDocument('Enclosure_D50_Technical_Drawing')
    draw.Label='Bản vẽ kỹ thuật vỏ trụ D50 — 3 tờ A3'
    for n in ('Rear_half','Front_half'):
        obj=draw.addObject('Part::Feature',n+'_Reference')
        obj.Shape=src.getObject(n).Shape.copy()
        obj.addProperty('App::PropertyString','SourceFile','Drawing'); obj.SourceFile=str(P)
        obj.addProperty('App::PropertyString','DrawingBasis','Drawing')
        obj.DrawingBasis='Static revision B snapshot. CAD projections and nominal dimension annotations in SVG sheets; regenerate when source changes.'
        obj.Visibility=False
    for i,name in enumerate(('01_Tong_the','02_Hai_nua_vo','03_Chi_tiet'),1):
        page=draw.addObject('TechDraw::DrawPage','Sheet_'+str(i))
        template=draw.addObject('TechDraw::DrawSVGTemplate','Template_'+str(i))
        template.Template=str(OUT/(name+'.svg'))
        page.Template=template
        page.Label=['01 — Tổng thể','02 — Hai nửa vỏ','03 — Chi tiết'][i-1]
    draw.recompute(); draw.saveAs(str(target))
else:
    # Rebuild generated sheet templates to reload changed SVG lettering.
    # Keep the document, pages and reference shapes already open.
    for i,name in enumerate(('01_Tong_the','02_Hai_nua_vo','03_Chi_tiet'),1):
        page=draw.getObject('Sheet_'+str(i))
        old=page.Template
        template=draw.addObject('TechDraw::DrawSVGTemplate','Refreshed_Template_'+str(i))
        template.Template=str(OUT/(name+'.svg'))
        page.Template=template
        if old: draw.removeObject(old.Name)
    draw.recompute(); draw.save()
App.setActiveDocument(draw.Name)
Gui.activeDocument().getObject('Sheet_1').show()
result={'file':draw.FileName,'pages':3,'format':'A3 landscape','pdf':str(OUT/'Ban_ve_ky_thuat_Vo_tru_D50.pdf'),'basis':'Static CAD-derived vector sheets, nominal dimensions; regenerate after geometry changes','source_assembly_unchanged':True}
