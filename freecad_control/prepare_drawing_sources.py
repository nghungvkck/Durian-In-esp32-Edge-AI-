from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part, TechDraw, json
ROOT=Path(r'D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai')
P=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd'
d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==P)
out=P.parent/'Technical_Drawing'; out.mkdir(exist_ok=True)
rear=d.Rear_half.Shape; front=d.Front_half.Shape
whole=rear.fuse(front)
def project(name,shape,normal,right):
    n=App.Vector(*normal); r=App.Vector(*right); u=n.cross(r)
    # Express in view coordinates, so top-view projection uses X/Y directly.
    mat=App.Matrix(r.x,r.y,r.z,0,u.x,u.y,u.z,0,n.x,n.y,n.z,0,0,0,0,1)
    s=shape.copy(); s.transformShape(mat)
    svg=TechDraw.projectToSVG(s,App.Vector(0,0,1))
    (out/(name+'.svgfrag')).write_text(svg,encoding='utf-8')
    return svg[:150]
views={}
for name,shape,n,r in [('front',whole,(0,1,0),(-1,0,0)),('rear',whole,(0,-1,0),(1,0,0)),('left',whole,(-1,0,0),(0,-1,0)),('top',whole,(0,0,1),(1,0,0)),('bottom',whole,(0,0,-1),(1,0,0)),('rear_inside',rear,(0,1,0),(-1,0,0)),('front_inside',front,(0,-1,0),(1,0,0)),('iso',whole,(1,-1,1),(1,1,0))]:
    # Normalize for isometric as well as orthogonal projections.
    nv=App.Vector(*n); nv.normalize(); rv=App.Vector(*r); rv.normalize()
    views[name]=project(name,shape,list(nv),list(rv))
# True section at X=0: take planar faces of the retained X-positive half.
kept=whole.common(Part.makeBox(30,60,205,App.Vector(0,-30,-1)))
faces=[f for f in kept.Faces if f.BoundBox.XLength<.00001 and abs(f.BoundBox.XMin)<.00001]
assert faces
section=Part.makeCompound(faces)
views['section_x0']=project('section_x0',section,(-1,0,0),(0,-1,0))
# Keep face loops separately for exact hatch regions, including their holes.
regions=[]
for f in faces:
    loops=[]
    for w in f.Wires:
        pts=w.discretize(Deflection=.015)
        loops.append([[-p.y,-p.z] for p in pts])
    regions.append(loops)
(out/'section_hatch.json').write_text(json.dumps(regions),encoding='utf-8')
(out/'geometry_metadata.json').write_text(json.dumps({'source':str(P),'source_objects':['Rear_half','Front_half'],'section_plane':'X=0','units':'mm','projection':'Third angle; independent views explicitly labeled','views':list(views)},indent=2),encoding='utf-8')
result={'views':views,'section_faces':len(faces),'project_doc':TechDraw.projectToSVG.__doc__}
