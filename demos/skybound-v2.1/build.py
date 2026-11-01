import os
from pathlib import Path
import math,struct,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from mesh import Mesh,words
from nearclip import clip_near
from hudfont import label
from flightmodel import sample_autopilot, sample_departure, sample_traverse
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
TOOL=Path(os.environ['SDCC_BIN']).resolve()
N=4352;LENGTH=960;F=170
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
    m.poly(p.tolist(),normal,0x80 if col in (9,10,14) else 0x8F if col==11 else col)
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
    def panel(x,y,w,h,z,c):m.poly([(x-w/2,y+h/2,z),(x+w/2,y+h/2,z),(x+w/2,y-h/2,z),(x-w/2,y-h/2,z)],[0,0,0],c)
    panel(0,-76,240,56,145,1)
    panel(0,-50,224,6,142,2)
    for i,x in enumerate([-63,-21,21,63]):
        panel(x,-66,37,37,140,2)
        panel(x,-66,32,32,138,0x88+i)
    for x in [-98,98]:
        panel(x,-67,16,24,138,2)
        for k in range(3):panel(x,-60-k*7,8,3,136,9 if k<2 else 8)
    for side in [-1,1]:
        m.poly([(side*110,-50,142),(side*126,82,142),(side*121,82,142),(side*106,-50,142)],[0,0,0],2)
    return clean(m)

def attitude():
    m=Mesh();m.poly([(-14,14,0),(14,14,0),(14,-14,0),(-14,-14,0)],[0,0,0],0x88);return clean(m)

def needle():
    m=Mesh();m.poly([(-1,-3,0),(0,12,0),(1,-3,0)],[0,0,0],8);return clean(m)

def chunk(index):
    m=Mesh();m.uv={};origin=road(index*LENGTH)
    def p(s,x,y=0):return point(s,x,y)-origin
    def box(q,x,y,sx,sy,sz,c):
        material=0x81 if c in (4,13) and sy>40 else 0x82 if c==15 and sy>30 else 0x80 if c==3 and sy>50 else c
        m.box(*p(q,x,y),sx,sy,sz,material)
        if material in (0x81,0x82):
            for i in range(len(m.f)-6,len(m.f)):
                ids,n,c=m.f[i]
                if abs(n[1])>.5:m.f[i]=(ids,n,3 if material==0x81 else 2)
        # Palette colors are independent hues, not a sequential lighting ramp.
        for i in range(len(m.f)-6,len(m.f)):
            ids,n,c=m.f[i]
            if not c&128:
                if c==5:c=5 if n[1]>0 else 4 if n[2] else 3
                m.f[i]=(ids,[0,0,0],c)
    def roof(q,x,y,w,d,h,c=3):
        pts=[(-w/2,0,-d/2),(w/2,0,-d/2),(w/2,0,d/2),(-w/2,0,d/2),(0,h,-d/2),(0,h,d/2)]
        pts=[p(q+z,x+xx,y+yy).tolist() for xx,yy,z in pts]
        for ids in [(0,4,5,3),(4,1,2,5),(0,1,4),(3,5,2)]:m.poly([pts[i] for i in ids],[0,0,0],0x83)
    def ring(q,x,levels,sides=8,cols=None):
        for n,((y,r),(yy,rr)) in enumerate(zip(levels,levels[1:])):
            for k in range(sides):
                t=k*2*math.pi/sides;u=(k+1)*2*math.pi/sides
                pts=[p(q+r*math.sin(t),x+r*math.cos(t),y),p(q+r*math.sin(u),x+r*math.cos(u),y),p(q+rr*math.sin(u),x+rr*math.cos(u),yy),p(q+rr*math.sin(t),x+rr*math.cos(t),yy)]
                m.poly([v.tolist() for v in pts],[0,0,0],(cols or [4])[n%len(cols)])
                if index==10 and x==1750 and cols and cols[0]==0x84:
                    u0=round(k*255/sides);u1=round((k+1)*255/sides)
                    v0=64+round((1-max(0,y)/1390)*63);v1=64+round((1-max(0,yy)/1390)*63)
                    m.uv[len(m.f)-1]=[u0,v0,u1,v0,u1,v1,u0,v1]
                if index in (25,26) and x==1700 and cols and cols[0]==0x84:
                    u0=round(k*255/sides);u1=round((k+1)*255/sides)
                    v0=96+round((1-max(0,y)/950)*31);v1=96+round((1-max(0,yy)/950)*31)
                    m.uv[len(m.f)-1]=[u0,v0,u1,v0,u1,v1,u0,v1]
    # A continuous green plain, water and a broad avenue; sparse geometry keeps movement smooth.
    xs=[-4500,-1400,-440,-130,130,440,1400,4500]
    for j in range(6 if index in (0,31) else 2):
        q=(-960 if index==0 else 29760)+j*320 if index in (0,31) else index*LENGTH+j*480;t=q+(320 if index in (0,31) else 480)
        for k,(x,xx) in enumerate(zip(xs,xs[1:])):
            col=[14,9,10,2,9,10,14][k]
            if index in (4,5,18,19,20,21,22,27,28):col=[11,11,11,11,11,11,11][k]
            if index in (1,2,3):col=[5,5,14,2,14,5,5][k]
            if index in (27,28,29,30):col=[11,11,9,2,9,11,11][k]
            if col in (9,10,14):col=0x8E if index in (14,15,29,30) else 0x8D if index in (1,3,6,10,11,25,26) else 0x8C
            face(m,[p(q,x,-15),p(q,xx,-15),p(t,xx,-15),p(t,x,-15)],col)
    q=index*LENGTH+480
    if index not in (0,31) and index in (7,8,9,12,13,14,15,16,17,23,24,29,30):
        for x in [-430,430]:
            box(q,x,-8,650,5,65,3)
        face(m,[p(q-320,-6,-12),p(q-320,6,-12),p(q+300,6,-12),p(q+300,-6,-12)],5)
    feature={0:0,7:1,8:2,9:4,10:8,11:9,12:13,13:12,14:24,15:28,16:21,17:19,23:40,24:13,29:24,30:24,31:0}.get(index,-1)
    if feature==0:
        # Tokyo airfield: asphalt runway, threshold marks, hangars and tower.
        for zz in range(-960,960,320):
            z=zz+(30720 if index==31 else 0)
            for x in [-122,122]:
                face(m,[p(z,x-3,-12),p(z,x+3,-12),p(z+320,x+3,-12),p(z+320,x-3,-12)],5)
        for zz in range(-800,900,160):
            z=zz+(30720 if index==31 else 0)
            face(m,[p(z,-7,-12),p(z,7,-12),p(z+70,7,-12),p(z+70,-7,-12)],5)
        for x in [-85,-55,55,85]:
            face(m,[p((30070 if index==31 else -650),x-8,-12),p((30070 if index==31 else -650),x+8,-12),p((30160 if index==31 else -560),x+8,-12),p((30160 if index==31 else -560),x-8,-12)],5)
        box((31000 if index==31 else 250),480,45,220,90,180,4)
        box((31200 if index==31 else 550),480,45,220,90,180,4)
        box((31400 if index==31 else 720),-420,85,40,170,40,5)
        box((31400 if index==31 else 720),-420,180,85,28,70,13)
    elif feature==2:
        # Distinct tapered tower, two observation decks and long antenna.
        ring(q,520,[(0,80),(280,43),(370,29),(390,76),(430,65),(450,27),(520,22),(540,48),(565,42),(580,17),(760,3)],6,[4,5,4,12,4,5,4,12,4,5])
        for x in [-550,-900]:box(q,x,115,180,230,210,4)
    elif feature==4:
        # Open lattice tower: four tapered legs, diagonal braces and two decks.
        def beam(a,b,width,col,crossed=False):
            a=np.array(a,float);b=np.array(b,float)
            for offset in ([np.array([width,0,0]),np.array([0,0,width])] if crossed else [np.array([width,0,width])]):
                m.poly([p(q+v[2],620+v[0],v[1]).tolist() for v in [a-offset,a+offset,b+offset,b-offset]],[0,0,0],col)
        corners=[(-1,-1),(1,-1),(1,1),(-1,1)]
        for x,z in corners:
            beam((x*115,z*0,z*115),(x*38,190,z*38),9,6)
            beam((x*38,190,z*38),(x*14,310,z*14),5,6)
        for j in range(4):
            x,z=corners[j];xx,zz=corners[(j+1)%4]
            beam((x*100,35,z*100),(xx*48,158,zz*48),4,6)
            beam((x*34,205,z*34),(xx*16,292,zz*16),3,5)
        box(q,620,181,108,15,108,5)
        box(q,620,198,96,14,96,6)
        box(q,620,311,55,14,55,5)
        ring(q,620,[(318,5),(340,5),(362,4),(384,3),(410,1)],4,[6,5,6,5])
        for x in [-600,1000]:box(q,x,120,200,240,260,4)
    elif feature in (8,9):
        if feature==8:
            ring(q,1750,[(-120,1700),(0,1600),(550,1050),(1000,520),(1350,170),(1390,90)],10,[0x84,0x84,0x84,0x84,0x84])
            ring(q,1750,[(1390,90),(1360,30)],10,[3])
        else:
            ring(q,-2200,[(0,1400),(480,400),(550,0)],6,[10,14])
    elif feature in (13,19):
        # Nagoya and Osaka castles: layered white walls, wide dark green roofs, gold finial.
        x=570 if feature==13 else -600
        box(q,x,35,360,70,330,3)
        for k in range(3):
            w=300-k*65;y=75+k*85
            box(q,x,y+27,w,54,w*.80,5)
            roof(q,x,y+54,w+70,w*.8+60,42,10)
        if feature==13:
            # Exactly two gold shachihoko, one at each end of the top roof ridge.
            for side in [-1,1]:
                z=q+side*90
                pts=[(-10,338,0),(10,338,0),(12,355,0),(4,363,0),(side*3,387,0),(-8,379,0),(-5,358,0),(-13,351,0)]
                for ids in [(0,1,2,7),(7,2,3,6),(6,3,4,5)]:
                    points=[p(z+pts[i][2],x+pts[i][0],pts[i][1]).tolist() for i in ids]
                    m.poly(points,[0,0,0],8);m.poly(points[::-1],[0,0,0],8)
        else:
            box(q,x,335,10,32,10,8)
            for side in [-1,1]:box(q,x+side*44,326,17,20,12,8)
    elif feature==21:
        # Open legs and stacked octagonal observation decks of Tsutenkaku.
        x=-480
        for dx in [-65,65]:
            for dz in [-65,65]:box(q+dz,x+dx,100,16,200,16,4)
        box(q,x,208,190,24,190,4)
        for dx in [-26,26]:
            for dz in [-26,26]:box(q+dz,x+dx,294,12,150,12,4)
        box(q,x,300,32,130,32,5)
        ring(q,x,[(365,55),(380,92),(402,92),(412,70),(426,88),(444,88),(458,40)],8,[4,11,4,4,11,4])
        ring(q,x,[(458,20),(495,16),(513,6),(540,1)],4,[5,4,5])
    elif feature==28:
        # Kyoto Tower: hotel podium and smooth white tapered observation tower.
        x=-1100
        box(q,x,40,360,80,250,4)
        ring(q,x,[(80,34),(240,24),(280,48),(310,46),(335,24),(380,3)],8,[5,5,4,5,5])
    elif feature>=23:
        for side in [-1,1]:
            for delta in [-270,0,270]:
                x=side*(300+(feature%2)*70)
                box(q+delta,x,36,140,72,190,15 if delta else 4)
                roof(q+delta,x,72,180,220,45,3)
    elif 0<=feature<6 or 11<=feature<=22:
        for side in [-1,1]:
            for k in range(3):
                h=80+((feature*7+k*13+(side+1)*5)%9)*25
                x=side*(420+k*230);z=q-260+k*220
                box(z,x,h/2,140+k*22,h,160,4 if k%2 else 13)
    elif feature>=0:
        for x in [-900,900]:ring(q,x,[(0,200),(230,0)],5,[10])
    # Region-specific silhouettes: secular landmarks and island scenery.
    if index==2:
        box(q,550,55,220,110,160,5);roof(q,550,110,260,200,55)
        box(q,550,175,70,80,65,5);roof(q,550,215,95,90,45)
        face(m,[p(q-34,530,180),p(q-34,570,180),p(q-34,570,205),p(q-34,530,205)],1)
    if index in (1,3,6):
        for x in [-1800,1800]:ring(q,x,[(0,1000),(450,600),(900,80)],8,[14,5])
    if index in (4,5,18,20,21,22,27,28):
        for dx,dz,r in [(-900,-150,400),(1100,230,540),(2400,-200,620)]:
            ring(q+dz,dx,[(0,r),(55,r*.85),(180,r*.35),(220,0)],6,[14,10,9])
    if index==19:
        for dx in [-460,460]:
            for dz in [-290,290]:box(q+dz,dx,180,24,360,24,5)
        box(q,0,85,1200,20,600,3)
        for dx in [-460,460]:
            for dz in [-290,290]:
                for off in [-220,0,220]:
                    m.poly([p(q+dz,dx,350).tolist(),p(q+off,0,100).tolist(),p(q+off+8,0,100).tolist()],[0,0,0],5)
    if index==23:
        ring(q,600,[(0,90),(320,45),(390,60),(430,35),(530,2)],6,[4,11,4,5])
    if index in (25,26):
        ring(q,1700,[(0,1500),(450,1000),(900 if index==26 else 700,420),(750 if index==26 else 560,200)],10,[0x84,0x84,3])
    if index in (29,30):
        for x in [-850,850]:
            box(q,x,70,12,140,12,3)
            for dx,dz in [(-100,0),(100,0),(0,-100),(0,100)]:
                m.poly([p(q,x,140).tolist(),p(q+dz,x+dx,115).tolist(),p(q+dz+20,x+dx+20,125).tolist()],[0,0,0],10)
    result=clean(m)
    assert len(result.v)<=255 and len(result.f)<=255,(index,len(result.v),len(result.f))
    return result,origin

def packmesh(m):
    d=m.data()
    uv=bytearray()
    for fi,(ids,normal,base) in enumerate(m.f):
        if fi in getattr(m,"uv",{}):
            uv.extend(m.uv[fi]);continue
        tile=base&15 if base&128 else 0;u=(tile%4)*64+2;v=(tile//4)*64+2
        pts=np.array([m.v[i] for i in ids],float)
        if base&128 and np.ptp(pts[:,1])>8 and tile!=0:
            axis=0 if np.ptp(pts[:,0])>=np.ptp(pts[:,2]) else 2
            xx=pts[:,axis];yy=pts[:,1]
            us=u+np.rint((xx-xx.min())/max(1,np.ptp(xx))*59)
            vs=v+59-np.rint((yy-yy.min())/max(1,np.ptp(yy))*59)
            uv.extend(int(a) for pair in zip(us,vs) for a in pair)
        else:uv.extend([u,v,u+59,v,u+59,v+59,u,v+59])
    d+=uv
    assert len(d)<=8192
    return bytearray(d+bytes(16384-len(d)))
def bitmap(im):
    a=np.array(im);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def build():
    banks=[bytearray(16384)]+[packmesh(cockpit()),packmesh(attitude()),packmesh(needle())]
    sky=Image.new('P',(256,256),12);sky.putpalette(sum([list(c) for c in COLORS],[])+[0]*720);d=ImageDraw.Draw(sky)
    d.rectangle((0,0,255,255),fill=12)
    # No painted horizon: all horizon tilt comes from polygon terrain.
    for x,y,w in ((25,28,45),(150,48,65),(85,90,35)):
        d.polygon([(x,y),(x+w,y),(x+w-12,y-3),(x+15,y-4)],fill=13)
    sky.save(OUT/'sky.png');b=bitmap(sky);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    hud=Image.new('P',(256,256));hud.putpalette(sky.getpalette());d=ImageDraw.Draw(hud)
    label(d,(4,0),'SKYBOUND / JAPAN ODYSSEY',fill=5)
    for i in range(15):
        y=16+i*16
        label(d,(5,y),['TOKYO / SKYTREE','MT FUJI / SNOW PEAK','NAGOYA / CASTLE','OSAKA / TSUTENKAKU','KYOTO / TOWER TURN'][min(i,4)],fill=5)
        d.line((4,y+13,251,y+13),fill=11)
    hud.save(OUT/'hud.png');b=bitmap(hud);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    chunks=[chunk(i) for i in range(32)]
    banks.extend(packmesh(m) for m,o in chunks)
    assert len(banks)==40
    frames=bytearray();stats=[]
    clip_banks={};clip_bank=114;clip_offset=0;clip_cache={}
    def store_clip(m):
        nonlocal clip_bank,clip_offset
        b=packmesh(clean(m));nv,nf,vb,fb=struct.unpack_from('<BBHH',b);payload=bytes(b[:6+vb+fb+nf*8])
        if payload in clip_cache:return clip_cache[payload]
        if clip_offset+len(payload)>16384:clip_bank+=1;clip_offset=0
        clip_banks.setdefault(clip_bank,bytearray(16384))[clip_offset:clip_offset+len(payload)]=payload
        result=(clip_bank,0x4000+clip_offset);clip_offset+=(len(payload)+1)&~1
        clip_cache[payload]=result;return result
    for f in range(N):
        state=sample_traverse(f,point)
        cp=state.position;s=state.route_s;roll=state.bank
        camera_fw=state.camera_direction
        camera_rt=unit(np.cross([0,1,0],camera_fw));camera_up=np.cross(camera_fw,camera_rt)
        right=camera_rt*math.cos(roll)+camera_up*math.sin(roll)
        up=camera_up*math.cos(roll)-camera_rt*math.sin(roll)
        view=np.array([right,up,camera_fw]);k=int(s//LENGTH)
        tframe=max(0,f-256)*1536/4096
        poses=[]
        indices=[0,1,2,3,4] if state.stage=='departure' else [27,28,29,30,31] if state.stage in ('approach','landing','stop') else list(range(max(0,min(27,k)),max(0,min(27,k))+5))
        indices=sorted(indices,key=lambda idx:np.linalg.norm(chunks[idx][1]-cp),reverse=True)
        addresses=[]
        for idx in indices:
            model_bank=8+idx;address=0x4000
            if True:
                mesh,origin=chunks[idx];packed=packmesh(mesh);uvstart=6+len(mesh.v)*6+len(mesh.f)*11
                clipped=clip_near(mesh,view,cp,origin,packed[uvstart:uvstart+len(mesh.f)*8])
                if clipped is not None and clipped.f:model_bank,address=store_clip(clipped)
            addresses.append(address)
            if idx>=32:poses.append((255,np.eye(3),np.array([0,0,2000])))
            else:poses.append((model_bank,view,view@(chunks[idx][1]-cp)))
        # Stable cockpit, bank-responsive attitude instrument and live analog needles.
        poses.append((1,np.eye(3),np.array([0,0,0])))
        def rz(a):return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
        poses.append((2,rz(-roll),np.array([-63,-66,136])))
        velocity=np.linalg.norm(sample_traverse(f+.2,point).position-sample_traverse(f,point).position)/.2
        speed_angle=-2.4+min(1.8,velocity/7.8)
        poses.append((3,rz(speed_angle),np.array([-21,-66,134])))
        alt_angle=-cp[1]/900*math.pi*2
        heading=-math.atan2(state.direction[0],state.direction[2])
        paired=needle()
        tri=np.array([[-1,-3,0],[0,12,0],[1,-3,0]],float)
        paired.poly([(rz(-alt_angle)@(np.array([42,0,0])+rz(heading)@v)).tolist() for v in tri],[0,0,0],8)
        gauge_bank,gauge_address=store_clip(paired)
        poses.append((gauge_bank,rz(alt_angle),np.array([21,-66,134])))
        rec=bytearray()
        for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
        rec+=bytes([p[0] for p in poses])+bytes(1)
        # V9968 sky displacement follows heading and pitch; road remains real 3D.
        yaw=math.atan2(camera_fw[0],camera_fw[2]);pitch=math.asin(camera_fw[1])
        rec+=words([int(48+46*math.sin(yaw)),512+max(0,min(16,int(8-pitch*20))),160,0])
        region=0 if k<7 else 1 if k<10 else 2 if k<12 else 3 if k<16 else 4 if k<23 else 5 if k<27 else 6
        hud_y=732 if state.stage=='departure' else 746 if state.stage in ('approach','landing') else 718 if state.stage=='stop' else [226,240,468,482,496,704,718][region]
        rec+=struct.pack('<HH',212,hud_y)
        rec+=bytes(256-len(rec));struct.pack_into("<9H",rec,238,*(addresses+[0x4000]*3+[gauge_address]));frames+=rec
        stats.append({'f':f,'segment':k,'stage':state.stage,'banks':[p[0] for p in poses]})
    banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384));assert len(banks)==108
    # Face records include normals/materials; UV bytes must also match exactly.
    topology_ids=[255]*64; topology_groups={}
    for bank in [1,2,3]+list(range(8,40)):
        nv,nf,vb,fb=struct.unpack_from('<BBHH',banks[bank])
        assert vb==nv*6 and fb==nf*11
        topology=bytes(banks[bank][6+vb:6+vb+fb+nf*8])
        topology_ids[bank]=topology_groups.setdefault(topology,len(topology_groups))
    (ROOT/'src/topology.inc').write_text('topology_ids:\n .db '+','.join(map(str,topology_ids))+'\n')
    import color256
    colors,resources=color256.make(COLORS,hud,ROOT,OUT)
    while len(banks)<256:banks.append(bytearray(16384))
    resources.update(clip_banks)
    assert max(resources)<256
    for bank,data in resources.items():banks[bank]=bytearray(data)
    pal=[round(v/255*31) for rgb in colors for v in rgb]
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
    subprocess.run([str(TOOL/'sdasz80.exe'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
    subprocess.run([str(TOOL/'sdldz80.exe'),'-n','-i','player','player.rel'],cwd=OUT,check=True)
    for line in (OUT/'player.ihx').read_text().splitlines():
        r=bytes.fromhex(line[1:]);assert sum(r)%256==0
        if r[3]==0:
            n=r[0];a=int.from_bytes(r[1:3],'big')
            if a>=0xE800:assert a+n<=0xF000;a=a-0xE800+0x4100
            banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
    rom=b''.join(banks);assert len(rom)==4194304
    (OUT/'SKYBOUND-JAPAN.ROM').write_bytes(rom)
    report={'frames':N,'rom_bytes':len(rom),'chunks':[{'v':len(m.v),'f':len(m.f)} for m,o in chunks],'sha256':hashlib.sha256(rom).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()


