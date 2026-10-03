import os
from pathlib import Path
import math,struct,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from mesh import Mesh,words
from hudfont import label
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
TOOL=Path(os.environ['SDCC_BIN']).resolve()
N=1536;LENGTH=960;F=170
COLORS=[(0,0,0),(32,32,32),(72,72,72),(112,112,112),(184,184,184),(255,255,255),(220,36,36),(255,108,36),(248,216,40),(96,148,88),(72,120,80),(32,92,164),(88,164,220),(172,216,248),(132,160,120),(128,104,112)]
def unit(v):return v/max(np.linalg.norm(v),1e-9)
def road(s):return np.array([800*math.sin(s/2400),0,s])
def axes(s):
    fw=unit(road(s+1)-road(s-1));rt=unit(np.cross([0,1,0],fw))
    return np.column_stack((rt,np.cross(fw,rt),fw))
def point(s,x,y=0):return road(s)+axes(s)@np.array([x,y,0])
def face(m,pts,col,normal=(0,0,0)):
    p=np.array(pts,float);n=np.cross(p[1]-p[0],p[2]-p[0])
    # Road polygons have an upward-facing winding.
    if n[1]<0:p=p[::-1]
    m.poly(p.tolist(),normal,0x80 if col in (9,10,14) else col)
def clean(m):
    vertices=[];mapping={};remap=[]
    for v in m.v:
        key=tuple(round(x) for x in v)
        if key not in mapping:mapping[key]=len(vertices);vertices.append(key)
        remap.append(mapping[key])
    m.v=vertices;m.f=[([remap[i] for i in ids],normal,base) for ids,normal,base in m.f]
    return m
def car(color):
    m=Mesh()
    # Original slender touring jet, faceted body, swept wings and tail.
    rings=[(-65,6,7),(-30,12,12),(25,10,10),(95,0,0)]
    for (z,w,h),(zz,ww,hh) in zip(rings,rings[1:]):
        r=[(-w,0,z),(0,h,z),(w,0,z),(0,-h,z)]
        t=[(-ww,0,zz),(0,hh,zz),(ww,0,zz),(0,-hh,zz)]
        for k in range(4):m.poly([r[k],t[k],t[(k+1)%4],r[(k+1)%4]],[0,0,0],[color,5,3,4][k])
    for side in (-1,1):
        pts=[(side*9,0,28),(side*100,-3,-35),(side*88,-3,-54),(side*8,0,-27)]
        m.poly(pts,[0,0,0],color);m.poly(pts[::-1],[0,0,0],4)
        pts=[(side*6,6,-42),(side*37,6,-65),(side*6,6,-62)]
        m.poly(pts,[0,0,0],color);m.poly(pts[::-1],[0,0,0],4)
    pts=[(0,5,-30),(0,38,-61),(0,5,-65)]
    m.poly(pts,[0,0,0],color);m.poly(pts[::-1],[0,0,0],color)
    m.box(0,12,8,12,9,25,11)
    return clean(m)
def cockpit():
    m=Mesh()
    # Camera-space dashboard: outside scenery banks around the fixed cockpit.
    m.poly([(-95,-62,140),(95,-62,140),(120,-95,140),(-120,-95,140)],[0,0,0],1)
    m.poly([(-95,-62,140),(-72,-53,140),(72,-53,140),(95,-62,140)],[0,0,0],3)
    for cx in (-58,-20,20,58):
        def panel(x,y,w,h,z,c):m.poly([(x-w/2,y+h/2,z),(x+w/2,y+h/2,z),(x+w/2,y-h/2,z),(x-w/2,y-h/2,z)],[0,0,0],c)
        panel(cx,-70,29,23,139,4)
        panel(cx,-70,25,19,137,1)
        panel(cx,-70,17,2,135,9 if cx<0 else 8)
        panel(cx,-68,2,10,133,5)
    for side in (-1,1):
        m.poly([(side*99,-62,140),(side*128,70,140),(side*122,70,140),(side*92,-62,140)],[0,0,0],3)
    return clean(m)
def chunk(index):
    m=Mesh();origin=road(index*LENGTH)
    def p(s,x,y=0):return point(s,x,y)-origin
    # Coast changes into a deep mountain valley: geometry, not a flat backdrop.
    valley=max(0,math.sin((index-8)/24*math.pi))
    xs=[-6000,-2200,-850,-260,-85,85,260,850,2200,6000]
    for j in range(7):
        s=index*LENGTH+j*(960/7);t=s+960/7
        def ht(q,x):
            if abs(x)<300:return -20
            return valley*max(0,min(2400,abs(x))-450)*.48*(.8+.2*math.sin(q/600))
        for k,(x,xx) in enumerate(zip(xs,xs[1:])):
            col=([11,11,12,9,11,9,9,10,10] if index<10 else [14,10,9,9,11,9,9,10,14])[k]
            if col==9 and (index+k)%4==0:col=10
            face(m,[p(s,x,ht(s,x)),p(s,xx,ht(s,xx)),p(t,xx,ht(t,xx)),p(t,x,ht(t,x))],col)
    s=index*LENGTH+480
    if index<4:
        for j in range(4):
            q=index*LENGTH+j*240
            face(m,[p(q,-100,0),p(q,100,0),p(q+240,100,0),p(q+240,-100,0)],2)
            face(m,[p(q+20,-4,2),p(q+20,4,2),p(q+140,4,2),p(q+140,-4,2)],5)
        for x in (-125,125):
            q=p(s,x,5);m.box(*q,8,10,18,8)
        if index==1:
            q=p(s,420,70);m.box(*q,180,140,320,4)
            q=p(s+170,370,170);m.box(*q,45,340,45,3)
            q=p(s+170,370,350);m.box(*q,90,50,80,11)
    elif index<10:
        for x,z in ((-560,100),(-780,600)):
            q=p(index*LENGTH+z,x,45);m.box(*q,160,90,260,4)
            q=p(index*LENGTH+z,x-130,190);m.box(*q,20,380,20,8)
            q=p(index*LENGTH+z,x-190,360);m.box(*q,260,18,20,8)
        q=p(s,500,45);m.box(*q,150,90,210,6)
    elif index in (13,21,27):
        # High viaducts cross the valley; fly over or beneath by phase.
        for x in (-550,550):
            q=p(s,x,210);m.box(*q,55,420,65,4)
        q=p(s,0,435);m.box(*q,1350,35,110,3)
        q=p(s,0,460);m.box(*q,1350,12,12,5)
    else:
        for x in (-550,650):
            q=p(s,x,55);m.box(*q,30,110,30,3)
            pts=[q+[-100,10,0],q+[100,10,0],q+[0,230,0]]
            m.poly([v.tolist() for v in pts],[0,0,0],10)
            m.poly([v.tolist() for v in pts[::-1]],[0,0,0],10)
    return clean(m),origin
def packmesh(m):
    d=m.data()
    uv=bytearray()
    for ids,normal,base in m.f:
        # UV winding follows the unchanged geometry vertex order.
        uv.extend([0,0,127,0,127,127,0,127])
    d+=uv
    assert len(d)<=8192
    return bytearray(d+bytes(16384-len(d)))
def bitmap(im):
    a=np.array(im);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def build():
    banks=[bytearray(16384)]+[packmesh(cockpit()),packmesh(car(8)),packmesh(car(5))]
    sky=Image.new('P',(256,256),12);sky.putpalette(sum([list(c) for c in COLORS],[])+[0]*720);d=ImageDraw.Draw(sky)
    d.rectangle((0,0,255,255),fill=12)
    # No painted horizon: all horizon tilt comes from polygon terrain.
    for x,y,w in ((25,28,45),(150,48,65),(85,90,35)):
        d.polygon([(x,y),(x+w,y),(x+w-12,y-3),(x+15,y-4)],fill=13)
    sky.save(OUT/'sky.png');b=bitmap(sky);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    hud=Image.new('P',(256,256));hud.putpalette(sky.getpalette());d=ImageDraw.Draw(hud)
    label(d,(4,0),'SKYBOUND V9968+GEO3D',fill=5)
    for i in range(15):
        y=16+i*16
        label(d,(5,y),f'ALT {80+i*50:04d}  AUTO FLIGHT',fill=5)
        d.line((4,y+13,251,y+13),fill=11)
    hud.save(OUT/'hud.png');b=bitmap(hud);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    # Convert AI-generated material to the existing SCREEN 5 palette.
    tex=Image.open(ROOT/'assets/terrain-generated.png').convert('RGB').resize((32,32),Image.Resampling.LANCZOS).resize((128,128),Image.Resampling.BILINEAR)
    a=np.asarray(tex,dtype=float);lum=a@np.array([.2126,.7152,.0722])
    lo,hi=np.percentile(lum,[10,95])
    ix=np.digitize(lum,[lo+(hi-lo)*.30,lo+(hi-lo)*.79])
    indexed=np.array([10,9,14],dtype=np.uint8)[ix]
    atlas=Image.fromarray(np.tile(indexed,(1,2))).convert('P')
    atlas.putpalette(sky.getpalette());atlas.save(OUT/'terrain-atlas.png')
    tb=bitmap(atlas)
    banks[2][8192:16384]=tb[:8192];banks[3][8192:16384]=tb[8192:]
    chunks=[chunk(i) for i in range(32)]
    banks.extend(packmesh(m) for m,o in chunks)
    assert len(banks)==40
    frames=bytearray();stats=[]
    for f in range(N):
        s=350+f*17.3
        def altitude(t):
            return 30+360*(1-math.exp(-max(0,t-90)/230))+180*math.sin(max(0,t-400)/200)
        def flight(t):
            ss=350+t*17.3
            return point(ss,170*math.sin(t/140),altitude(t))
        cp=flight(f)
        forward=unit(flight(f+3)-flight(f-3))
        rt=unit(np.cross([0,1,0],forward));uu=np.cross(forward,rt)
        roll=.40*math.sin(f/155)*min(1,max(0,(f-100)/180))
        right=rt*math.cos(roll)+uu*math.sin(roll);up=uu*math.cos(roll)-rt*math.sin(roll)
        view=np.array([right,up,forward]);k=int(s//LENGTH)
        poses=[]
        for j in (3,2,1,0):
            idx=k+j
            if idx>=32:poses.append((255,np.eye(3),np.array([0,0,2000])))
            else:poses.append((8+idx,view,view@(chunks[idx][1]-cp)))
        # Escort jets use world-space formation positions; cockpit nose stays relative to pilot.
        for offset,bank in ((-220,2),(250,3)):
            pos=flight(f+28)+rt*offset+uu*(35+30*math.sin(f/85+bank))
            poses.append((bank,view@np.column_stack((rt,uu,forward)),view@(pos-cp)))
        poses.append((1,np.eye(3),np.array([0,0,0])))
        rec=bytearray()
        for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
        rec+=bytes([p[0] for p in poses])+bytes(1)
        # V9968 sky displacement follows heading and pitch; road remains real 3D.
        yaw=math.atan2(forward[0],forward[2]);pitch=math.asin(forward[1])
        rec+=words([int(48+yaw*60),512+int(24-pitch*85),160,0])
        speed=max(0,min(14,round((altitude(f)-80)/50)));rec+=struct.pack('<HH',768,768+16+speed*16)
        rec+=bytes(256-len(rec));frames+=rec
        stats.append({'f':f,'segment':k,'banks':[p[0] for p in poses]})
    banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384));assert len(banks)==64
    # Face records include normals/materials; UV bytes must also match exactly.
    topology_ids=[255]*64; topology_groups={}
    for bank in [1,2,3]+list(range(8,40)):
        nv,nf,vb,fb=struct.unpack_from('<BBHH',banks[bank])
        assert vb==nv*6 and fb==nf*11
        topology=bytes(banks[bank][6+vb:6+vb+fb+nf*8])
        topology_ids[bank]=topology_groups.setdefault(topology,len(topology_groups))
    (ROOT/'src/topology.inc').write_text('topology_ids:\n .db '+','.join(map(str,topology_ids))+'\n')
    pal=[]
    for rgb in COLORS:
        r,g,b=[round(c/255*7) for c in rgb];pal.extend([(r<<4)|b,g])
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
    subprocess.run([str(TOOL/'sdasz80.exe'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
    subprocess.run([str(TOOL/'sdldz80.exe'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
    for line in (OUT/'player.ihx').read_text().splitlines():
        r=bytes.fromhex(line[1:]);assert sum(r)%256==0
        if r[3]==0:
            n=r[0];a=int.from_bytes(r[1:3],'big')
            if a>=0xE800:assert a+n<=0xF000;a=a-0xE800+0x4100
            banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
    rom=b''.join(banks);assert len(rom)==1048576
    (OUT/'SKYBOUND.ROM').write_bytes(rom)
    report={'frames':N,'rom_bytes':len(rom),'chunks':[{'v':len(m.v),'f':len(m.f)} for m,o in chunks],'sha256':hashlib.sha256(rom).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
