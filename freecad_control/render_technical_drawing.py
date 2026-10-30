"""Compose dimensioned CAD vector projections into three A3 drawing sheets.

Run with the local Python (PyQt5). Geometry is prepared inside FreeCAD first.
Dimensions are annotations of this revision, not associative constraints.
"""
from pathlib import Path
import os, re, json, math, html
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QByteArray, QRectF, QMarginsF
from PyQt5.QtGui import QImage, QPainter, QPdfWriter, QPageSize, QPageLayout
from PyQt5.QtSvg import QSvgRenderer

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'3D/Enclosure_USB_Near_Wall_D50/Technical_Drawing'
HATCH=json.loads((OUT/'section_hatch.json').read_text())
# Larger lettering throughout the sheets, including dimension numerals.
TEXT_SCALE=1.4
F=[]
def add(s): F.append(s)
def text(x,y,s,size=2.7,anchor='start',rotate=None,weight='normal'):
    size*=TEXT_SCALE
    tr=f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ''
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"{tr}>{html.escape(str(s))}</text>')
def line(x1,y1,x2,y2,width=.18,dash=None):
    da=f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#111" stroke-width="{width}"{da}/>')
def rect(x,y,w,h,width=.18,fill='none'):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#111" stroke-width="{width}"/>')
def circle(x,y,r,width=.18):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#111" stroke-width="{width}"/>')
def arrow(x,y,dx,dy):
    # Tip at measured position; a 1.5 mm closed arrowhead.
    length=math.hypot(dx,dy); dx/=length; dy/=length
    add(f'<path d="M{x},{y} l{dx*1.5-dy*.45},{dy*1.5+dx*.45} l{dy*.9},{-dx*.9} Z" fill="#111"/>')
def dh(x1,x2,feature_y,y,label):
    for x in (x1,x2): line(x,feature_y,x,y+(-1 if y<feature_y else 1),.13)
    line(x1,y,x2,y,.15); arrow(x1,y,1,0); arrow(x2,y,-1,0)
    text((x1+x2)/2,y-1.2,label,2.8,'middle')
def dv(y1,y2,feature_x,x,label):
    for y in (y1,y2): line(feature_x,y,x+(-1 if x<feature_x else 1),y,.13)
    line(x,y1,x,y2,.15); arrow(x,y1,0,1); arrow(x,y2,0,-1)
    text(x-1.5,(y1+y2)/2,label,2.8,'middle',-90)
def center(x,y,rx,ry):
    line(x-rx,y,x+rx,y,.13,'5 1 1 1'); line(x,y-ry,x,y+ry,.13,'5 1 1 1')
def leader(points,label,align='start',size=2.7):
    for a,b in zip(points,points[1:]): line(*a,*b,.16)
    a,b=points[0],points[1]; arrow(*a,b[0]-a[0],b[1]-a[1])
    x,y=points[-1]; text(x+(1 if align=='start' else -1),y-1,label,size,align)
def caption(x,y,title,scale='1:1'):
    text(x,y,title,3.1,'middle',weight='bold'); text(x,y+4.2,'TỶ LỆ '+scale,2.4,'middle')
def geom(name,cx,cy,scale=1,clip=None):
    raw=(OUT/(name+'.svgfrag')).read_text()
    raw=re.sub(r'\s+id\s*=\s*"[^"]*"','',raw)
    raw=raw.replace('stroke-width="1.0"',f'stroke-width="{.26/scale}"')
    cliptext=f' clip-path="url(#{clip})"' if clip else ''
    add(f'<g{cliptext}><g transform="translate({cx},{cy}) scale({scale})">{raw}</g></g>')
def section(cx,cy,scale=1,clip=None):
    # QtSvg omits SVG patterns and clip paths. Emit real hatch segments and
    # use CAD-cropped detail projections so PDF and SVG have identical marks.
    bounds={'cap':(-201,-168),'floor':(-15,0)}.get(clip,(-201,0))
    add(f'<g transform="translate({cx},{cy}) scale({scale})">')
    for region in HATCH:
        pts=[p for loop in region for p in loop]
        k0=math.floor(min(y-x for x,y in pts)/1.5)
        k1=math.ceil(max(y-x for x,y in pts)/1.5)
        for ki in range(k0,k1+1):
            k=ki*1.5; hits=[]
            for loop in region:
                for a,b in zip(loop,loop[1:]+loop[:1]):
                    den=(b[1]-a[1])-(b[0]-a[0])
                    if abs(den)<1e-10: continue
                    t=(k-(a[1]-a[0]))/den
                    if 0<=t<1: hits.append(a[0]+t*(b[0]-a[0]))
            hits.sort()
            for a,b in zip(hits[::2],hits[1::2]):
                a=max(a,bounds[0]-k); b=min(b,bounds[1]-k)
                if b>a+1e-7:
                    add(f'<path d="M{a:.4f},{a+k:.4f} L{b:.4f},{b+k:.4f}" stroke="#666" stroke-width="{.12/scale}"/>')
    add('</g>')
    name={'cap':'cap_section','floor':'floor_section'}.get(clip,'section_x0')
    geom(name,cx,cy,scale)
def table(x,y,width,headers,rows,colwidths=None,rowh=7):
    ws=colwidths or [width/len(headers)]*len(headers)
    rect(x,y,width,rowh*(len(rows)+1),.25)
    for i in range(1,len(rows)+1): line(x,y+i*rowh,x+width,y+i*rowh,.14)
    xx=x
    for j,w in enumerate(ws):
        if j: line(xx,y,xx,y+(len(rows)+1)*rowh,.14)
        text(xx+1.8,y+rowh*.68,headers[j],2.5,weight='bold')
        for i,row in enumerate(rows): text(xx+1.8,y+(i+1)*rowh+rowh*.68,row[j],2.45)
        xx+=w
def notes(x,y,lines,size=2.6,step=4.5):
    for i,s in enumerate(lines): text(x,y+step*i,s,size)
def frame(number,title,subtitle):
    global F; F=[]
    add('<svg xmlns="http://www.w3.org/2000/svg" xmlns:freecad="http://www.freecadweb.org/wiki/index.php?title=Svg_Namespace" width="420mm" height="297mm" viewBox="0 0 420 297">')
    add('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="2" height="2"><path d="M-1,1 L1,-1 M0,2 L2,0 M1,3 L3,1" stroke="#777" stroke-width=".10"/></pattern><clipPath id="cap"><rect x="18" y="42" width="176" height="104"/></clipPath><clipPath id="floor"><rect x="18" y="208" width="176" height="46"/></clipPath><clipPath id="sound"><rect x="270" y="189" width="66" height="66"/></clipPath></defs>')
    add('<g font-family="DejaVu Sans,Arial,sans-serif" fill="#111">')
    rect(7,7,406,283,.5)
    text(12,17,'VỎ THU ÂM TIẾNG GÕ  |  Ø50 × 201',4.5,weight='bold')
    text(12,23,title,3.4); text(408,16,f'{number:02d} / 03',4,'end',weight='bold')
    text(408,23,subtitle,2.45,'end'); line(7,28,413,28,.3)
    # Bottom title block, consistently shared across all sheets.
    line(7,271,413,271,.35)
    for x in (185,267,330,375): line(x,271,x,290,.2)
    text(11,276,'TÊN CHI TIẾT / CỤM',2.1); text(11,282,'Vỏ trụ hai nửa — khe tâm 20 × 3',3.3,weight='bold')
    text(11,287,'Nguồn: Enclosure_USB_Near_Wall_D50.FCStd',2.2)
    text(189,276,'MÃ BẢN VẼ',2.1); text(189,282,f'DEA-ENC-050-{number:02d}',3.2,weight='bold'); text(189,287,'REV B · 30/10/2026',2.2)
    text(271,276,'ĐƠN VỊ / KHỔ',2.1); text(271,282,'mm / A3 ngang',2.8); text(271,287,'In 100% kích thước trang',2.05)
    text(334,276,'TỶ LỆ',2.1); text(334,282,'Theo hình',2.8); text(334,287,'Kích thước danh nghĩa',2.05)
    text(379,276,'TỜ',2.1); text(379,283,f'{number} / 3',4,weight='bold')
def finish(name):
    add('</g></svg>'); s='\n'.join(F)
    (OUT/(name+'.svg')).write_text(s,encoding='utf-8'); return s

frame(1,'TỔNG THỂ — HÌNH CHIẾU VÀ MẶT CẮT','Chỉ thể hiện hai nửa vỏ nhựa · Không gồm linh kiện')
# Three aligned upright views, 1:1.
geom('front',57,246); center(57,145.5,28,106)
geom('left',143,246); center(143,145.5,28,106)
section(231,246); center(231,145.5,28,106)
dh(32,82,45,36,'Ø50'); dv(45,246,32,18,'201')
dv(50,70,57,91,'20'); dv(45,50,57,102,'5')
leader([(57,50),(76,57),(83,57)],'2 × Ø4',size=2.5)
leader([(57,90),(73,100),(86,100)],'3 × Ø4,6',size=2.5)
# Datum and button levels (dimensions in schedule to avoid a crowded chain).
text(86,111,'Z140 / 148 / 156',2.4)
line(57,40,57,249,.32,'8 2 1 2'); arrow(57,41,1,0); arrow(57,249,1,0)
text(61,41,'A',3.2,weight='bold'); text(61,251,'A',3.2,weight='bold')
dh(206,256,45,36,'50'); dh(209,253,130,137,'44 — khoang chính')
dv(45,78,256,269,'33'); dv(243,246,256,269,'3')
leader([(232.5,57),(255,62),(269,62)],'Khe 3 (xem tờ 3)',size=2.4)
leader([(207,115),(194,122),(185,122)],'Vách 3',align='end',size=2.4)
caption(57,258,'MẶT TRƯỚC (+Y)'); caption(143,258,'MẶT HÔNG (−X)'); caption(231,258,'MẶT CẮT A–A · X=0')
geom('top',341,73); center(341,73,29,29)
dh(331,351,71.5,38,'20'); dv(71.5,74.5,351,377,'3')
leader([(341,73),(379,89),(402,89)],'Khe đúng tâm',align='end',size=2.5)
caption(341,106,'NHÌN TỪ ĐỈNH (+Z)')
geom('iso',342,242,.58)
caption(342,253,'HÌNH TRỤC ĐO','≈ 1:1,72')
notes(286,117,['Gốc O: tâm đáy cần gạt, Z=0; đỉnh Z201.', 'Mặt chia Y=0; mặt cắt A–A tại X=0.', 'Hình chiếu bố trí độc lập theo nhãn.', 'Gạch mặt cắt: vật liệu vỏ.', 'Mặt cổng USB X−23; lùi mép ≈1,4.'],2.45,4.4)
svg1=finish('01_Tong_the')

frame(2,'CHI TIẾT HAI NỬA VỎ — GIÁ LẮP VÀ LỖ GHÉP','Hình chiếu phía trong · Đường nét lấy từ BRep hiện tại')
geom('rear_inside',67,246); center(67,145.5,28,106)
geom('front_inside',171,246); center(171,145.5,28,106)
dh(46,88,232,257,'42'); dh(150,192,232,257,'42')
dv(80,232,46,28,'152'); dv(149,232,46,37,'83')
dv(80,149,88,104,'69')
for x in (46,88,150,192):
    for y in (232,149,80): center(x,y,3,3)
leader([(171,83),(194,104),(210,104)],'2 × pilot Ø2',size=2.5)
leader([(171,83),(190,71),(209,71)],'Trụ Ø6,8',size=2.5)
leader([(67,87),(90,101),(107,101)],'Giá micro',size=2.5)
caption(67,265,'NỬA SAU — Rear_half')
caption(171,265,'NỬA TRƯỚC — Front_half')
text(231,39,'BẢNG LỖ GHÉP THÂN',3.5,weight='bold')
table(231,44,171,['Vị trí tâm','Nửa trước','Nửa sau'],[
    ('X±21, Z14','Ø3,4 / bậc Ø6,4','Pilot Ø2,6'),
    ('X±21, Z97','Ø3,4 / bậc Ø6,4','Pilot Ø2,6'),
    ('X±21, Z166','Ø3,4 / bậc Ø6,4','Pilot Ø2,6'),
], [58,61,52],rowh=9)
notes(231,86,['Tổng 6 vị trí ghép; trục lỗ song song Y.', 'Chưa chọn vít và dung sai lắp thực tế.', 'Lỗ Ø4 trên đỉnh là nhóm riêng (tờ 1/3).'],2.6,5)
text(231,111,'LỖ / GIÁ NÚT VÀ MICRO',3.5,weight='bold')
table(231,116,171,['Chi tiết','Thông số danh nghĩa'],[
    ('Lỗ bấm nút','3 × Ø4,6; X0; Z140 / 148 / 156'),
    ('Trụ gá module nút','2 × Ø6,8; pilot Ø2; Z133 / 163'),
    ('Khoảng tâm trụ nút','30; tâm X0'),
    ('Vít micro (pilot)','2 × Ø1,6; X±7,9; Z159'),
    ('Lỗ âm thành sau','Ø1,2 + 6 × Ø0,9; xem tờ 3'),
    ('Đường ghép vỏ','Lưỡi / rãnh theo mô hình CAD'),
], [65,106],rowh=8)
text(231,185,'GHI CHÚ CHẾ TẠO',3.5,weight='bold')
notes(231,192,[
    '1. Các kích thước ghi trên bản vẽ tính bằng mm.',
    '2. Kích thước danh nghĩa trích từ CAD, chưa gán dung sai.',
    '3. Vật liệu, hướng in, co ngót và độ hở lắp chưa chốt.',
    '4. Giá đỡ / đường dẫn dây còn lại: theo FCStd và STEP.',
    '5. Không in chung PCB, vít, dây hoặc đệm mềm.',
    '6. Chưa thử in, lắp thực tế hoặc kiểm tra lực ghép.',
    '7. Vùng đỉnh đặc: đặt infill phù hợp trong slicer.',
    '8. Không đo kích thước trực tiếp trên ảnh xem trước.',
],2.65,6.2)
svg2=finish('02_Hai_nua_vo')

frame(3,'CHI TIẾT PHÓNG TO — ĐỈNH, KHE, ĐÁY VÀ LỖ ÂM','Kích thước được ghi ở giá trị thật, không nhân theo tỷ lệ')
# Cap section enlargement, 3:1; cut top at y45, Z168 at y144.
section(105,648,3,'cap')
center(105,96,80,55)
dh(30,180,45,36,'50'); dv(45,144,180,198,'33')
dv(60,120,30,18,'20')
leader([(30,60),(42,69),(66,69)],'2 × Ø4 xuyên Y',size=2.7)
leader([(109.5,45),(134,54),(171,54)],'Khe rộng 3',align='end',size=2.7)
text(105,151,'CHI TIẾT B — MẶT CẮT ĐỈNH A–A',3,'middle',weight='bold')
text(105,156,'TỶ LỆ 3:1 · Z168–201',2.5,'middle')
notes(23,168,['Đoạn Z168–201 cao 33; phần thêm Z171–201 cao 30.',
    'Tâm hai lỗ tại Z176 và Z196; tâm trên cách đỉnh 5.',
    'Khe tâm giao hai lỗ Ø4, mở vào khoang phía dưới.'],2.5,5)
# True top view, 2:1.
geom('top',303,94,2); center(303,94,55,55)
dh(283,323,91,34,'20'); dv(91,97,323,363,'3')
leader([(303,94),(368,113),(398,113)],'Tâm X0 / Y0',align='end')
text(303,154,'CHI TIẾT C — KHE TRÊN MẶT ĐỈNH',3,'middle',weight='bold')
text(303,159,'TỶ LỆ 2:1',2.5,'middle')
# Floor section, 3:1, only bottom Z0..15.
section(105,253,3,'floor')
dv(244,253,30,18,'3')
leader([(105,248),(140,231),(191,231)],'Đáy giữ nguyên',align='end')
text(105,263,'CHI TIẾT D — ĐÁY CẦN GẠT · 3:1',3,'middle',weight='bold')
# Acoustic pattern, explicit nominal geometry verified from cylindrical faces.
cx,cy,s=282,213,12
circle(cx,cy,.6*s,.3)
for a in range(0,360,60):
    x=cx+1.2*s*math.cos(math.radians(a)); y=cy-1.2*s*math.sin(math.radians(a))
    circle(x,y,.45*s,.3)
circle(cx,cy,1.2*s,.13); center(cx,cy,24,24)
leader([(cx+7.2,cy),(323,203),(399,203)],'1 × Ø1,2',align='end')
leader([(cx+19.8,cy),(324,215),(399,215)],'6 × Ø0,9 đều 60°',align='end')
leader([(cx+14.4,cy),(323,229),(399,229)],'Vòng tâm Ø2,4',align='end')
text(303,250,'CHI TIẾT E — LỖ ÂM THÀNH SAU',3,'middle',weight='bold')
text(303,255,'TỶ LỆ 12:1 · Tâm X0 / Z159',2.5,'middle')
text(230,172,'Đáy: hốc ngoài 24,2 × 10,2; cửa trong 13,4 × 6,4.',2.5)
text(230,178,'Tâm hốc X0 / Y16; pilot Ø1,6 tại X±9,5 / Y16.',2.5)
svg3=finish('03_Chi_tiet')

app=QApplication.instance() or QApplication([])
writer=QPdfWriter(str(OUT/'Ban_ve_ky_thuat_Vo_tru_D50.pdf'))
writer.setResolution(254)
writer.setPageSize(QPageSize(QPageSize.A3))
writer.setPageOrientation(QPageLayout.Landscape)
writer.setPageMargins(QMarginsF(0,0,0,0),QPageLayout.Millimeter)
writer.setTitle('Vỏ trụ Ø50 × 201 — Bản vẽ kỹ thuật Rev B')
writer.setCreator('CAD projections: FreeCAD 1.1.4; dimensioned revision B')
painter=QPainter(writer)
for i,svg in enumerate((svg1,svg2,svg3)):
    renderer=QSvgRenderer(QByteArray(svg.encode()))
    assert renderer.isValid(), 'Invalid SVG sheet'
    if i: writer.newPage()
    renderer.render(painter,QRectF(0,0,writer.width(),writer.height()))
    im=QImage(2520,1782,QImage.Format_ARGB32); im.fill(0xffffffff)
    ip=QPainter(im); ip.setRenderHint(QPainter.Antialiasing); renderer.render(ip); ip.end()
    assert im.save(str(OUT/f'preview_{i+1:02d}.png'))
painter.end()
print(json.dumps({'pdf':str(OUT/'Ban_ve_ky_thuat_Vo_tru_D50.pdf'),'sheets':3,'page_mm':[420,297],'svg_and_preview':True},ensure_ascii=False))
