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
COLORS=[(0,0,0),(32,32,32),(72,72,72),(112,112,112),(184,184,184),(255,255,255),(220,36,36),(255,108,36),(248,216,40),(72,144,72),(32,80,48),(32,92,164),(88,164,220),(172,216,248),(96,128,144),(128,104,112)]
def unit(v):return v/max(np.linalg.norm(v),1e-9)
def road(s):return np.array([660*math.sin(s/1900)+390*math.sin(s/4200),100*math.sin(s/1100)+160*math.sin(s/3600),s])
def axes(s):
    forward=unit(road(s+1)-road(s-1));right=unit(np.cross([0,1,0],forward));up=np.cross(forward,right)
    bank=.19*math.sin(s/1650)
    return np.column_stack((right*math.cos(bank)+up*math.sin(bank),up*math.cos(bank)-right*math.sin(bank),forward))
def point(s,x,y=0):return road(s)+axes(s)@np.array([x,y,0])
def face(m,pts,col,normal=(0,0,0)):
    p=np.array(pts,float);n=np.cross(p[1]-p[0],p[2]-p[0])
    # Road polygons have an upward-facing winding.
    if n[1]<0:p=p[::-1]
    m.poly(p.tolist(),normal,col)
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
    m.box(0,15,-8,24,16,80,color)
    for side in (-1,1):m.box(side*19,14,-13,16,15,54,6 if color==7 else color)
    # Sloping nose and shoulder facets, tapered forward silhouette.
    m.poly([(-18,28,13),(18,28,13),(10,19,68),(-10,19,68)],[0,0,0],color)
    m.poly([(-18,28,13),(-10,19,68),(-10,12,68),(-18,10,13)],[0,0,0],6 if color==7 else 3)
    m.poly([(18,10,13),(10,12,68),(10,19,68),(18,28,13)],[0,0,0],color)
    m.box(0,26,-5,19,9,26,1)
    m.box(0,33,-5,10,9,11,5) # driver's helmet
    for side in (-1,1):
        m.box(side*27,13,33,14,25,25,1)
        m.box(side*29,14,-35,19,27,30,1)
        m.box(side*30,14,-35,20,10,12,3)
        m.box(side*24,8,34,25,4,6,4)
        m.box(side*21,9,-35,30,4,7,4)
    m.box(0,38,-51,69,6,16,color)
    m.box(0,10,60,64,5,13,4)
    m.box(0,29,-52,10,9,8,6)
    m.box(0,16,-50,22,12,3,1)
    return clean(m)
def chunk(index):
    m=Mesh();origin=road(index*LENGTH)
    def p(s,x,y=0):return point(s,x,y)-origin
    for j in range(8):
        s=index*LENGTH+j*120;t=s+120
        strips=[(-1450,-240,11),(-240,-216,4),(-216,-202,6 if j%2==0 else 5),(-202,202,2),(202,216,6 if j%2==0 else 5),(216,240,4),(240,1450,9)]
        for a,b,c in strips:face(m,[p(s,a),p(s,b),p(t,b),p(t,a)],c)
        if j%2==0:face(m,[p(s+22,-3,1),p(s+22,3,1),p(t-25,3,1),p(t-25,-3,1)],5)
        # Guardrails have real height and parallax.
        for side in (-1,1):
            x=side*243
            pts=[p(s,x,15),p(t,x,15),p(t,x,29),p(s,x,29)]
            if side<0:pts.reverse()
            m.poly([v.tolist() for v in pts],[0,0,0],4)
    # Different districts: pylons, trees, grandstands and track signs.
    s=index*LENGTH+480
    if index in (0,9,20,28):
        for x in (-310,310):
            q=p(s,x,75);m.box(*q,24,150,30,3)
        q=p(s,0,157);m.box(*q,650,28,24,11)
        q=p(s,0,157)+[0,0,-13];m.box(*q,160,14,2,8)
        for x in (-190,-140,140,190):
            q=p(s,x,157)+[0,0,-14];m.box(*q,24,14,2,5)
    elif index in (1,10,26):
        q=p(s,390,36);m.box(*q,180,72,390,3)
        for y,z in ((75,0),(105,45)):
            q=p(s+z,400,y);m.box(*q,200,18,390,4)
        for z in (360,435,510,585):
            q=p(index*LENGTH+z,400,124);m.box(*q,150,7,26,6 if z%2 else 11)
    elif index in (5,17,25):
        # Harbour cranes and warehouses; functionless but geometric landmarks.
        q=p(s,-630,60);m.box(*q,230,120,250,4)
        q=p(s,-470,180);m.box(*q,26,360,28,8)
        q=p(s,-610,335);m.box(*q,340,20,28,8)
        q=p(s,-740,235);m.box(*q,6,190,6,3)
    elif index in (7,16,23):
        # A hillside rise, with a tall beacon on the headland.
        q=p(s,580,115);m.box(*q,75,230,80,4)
        q=p(s,580,240);m.box(*q,100,24,105,6)
        q=p(s,580,273);m.box(*q,55,42,60,11)
    else:
        for z,x in ((170,340),(580,420)):
            q=p(index*LENGTH+z,x,65)
            m.box(*q,12,130,12,3)
            for dy,w in ((10,80),(55,55)):
                c=q+[0,dy,0]
                m.poly([(c+[a,b,d]).tolist() for a,b,d in ((-w,-25,0),(w,-25,0),(0,70,0))],[0,0,0],10)
                m.poly([(c+[a,b,d]).tolist() for a,b,d in ((0,-25,w),(0,-25,-w),(0,70,0))],[0,0,0],9)
    m=clean(m)
    assert len(m.v)<=255,(index,len(m.v))
    return m,origin
def packmesh(m):
    d=m.data();assert len(d)<=16384
    return bytearray(d+bytes(16384-len(d)))
def bitmap(im):
    a=np.array(im);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def build():
    banks=[bytearray(16384)]+[packmesh(car(c)) for c in (7,8,11)]
    sky=Image.new('P',(256,256),12);sky.putpalette(sum([list(c) for c in COLORS],[])+[0]*720);d=ImageDraw.Draw(sky)
    d.rectangle((0,0,255,58),fill=11);d.rectangle((0,59,255,104),fill=12);d.rectangle((0,105,255,150),fill=13)
    d.ellipse((185,55,213,83),fill=5)
    for base,amp,col,phase in ((149,26,14,0),(161,19,10,2)):
        pts=[(x,base-int(amp*(.5+.3*math.sin(x*.06+phase)+.2*math.sin(x*.15)))) for x in range(257)]
        d.polygon(pts+[(256,256),(0,256)],fill=col)
    sky.save(OUT/'sky.png');b=bitmap(sky);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    hud=Image.new('P',(256,256));hud.putpalette(sky.getpalette());d=ImageDraw.Draw(hud)
    label(d,(4,0),'VECTOR/RUSH V9968+GEO3D',fill=5)
    for i in range(15):
        y=16+i*16
        label(d,(5,y),f'{240+i*3} KM/H   LAP 01   DEMO',fill=5)
        d.line((4,y+13,251,y+13),fill=11)
    hud.save(OUT/'hud.png');b=bitmap(hud);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    chunks=[chunk(i) for i in range(32)]
    banks.extend(packmesh(m) for m,o in chunks)
    assert len(banks)==40
    frames=bytearray();stats=[]
    for f in range(N):
        s=350+f*17.3
        cp=point(s,0,125);ax=axes(s+160)
        forward=unit(ax[:,2]-.10*ax[:,1]);camera_up=unit(np.array([0,1,0])*.65+ax[:,1]*.35)
        right=unit(np.cross(camera_up,forward));up=np.cross(forward,right)
        view=np.array([right,up,forward])
        k=int(s//LENGTH)
        poses=[]
        for j in (3,2,1,0):
            idx=k+j
            if idx>=32:poses.append((255,np.eye(3),np.array([0,0,2000])))
            else:poses.append((8+idx,view,view@(chunks[idx][1]-cp)))
        carstates=[]
        positions=[(s+250,70*math.sin(math.pi*f/N),1),
                   (s+250+500*math.cos(f*.004)-70,-100,2),
                   (s+250+450+220*math.sin(f*.009),110,3)]
        for cs,lane,bank in positions:
            pos=point(cs,lane,4);mat=axes(cs)
            cv=view@(pos-cp)
            carstates.append((bank if cv[2]>90 else 255,view@mat,cv))
        carstates.sort(key=lambda t:t[2][2],reverse=True);poses.extend(carstates)
        rec=bytearray()
        for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
        rec+=bytes([p[0] for p in poses])+bytes(1)
        # V9968 sky displacement follows heading and pitch; road remains real 3D.
        yaw=math.atan2(forward[0],forward[2]);pitch=math.asin(forward[1])
        rec+=words([int(48+yaw*60),512+int(24-pitch*85),160,0])
        speed=round(7+6*math.sin(f*.01));rec+=struct.pack('<HH',768,768+16+speed*16)
        rec+=bytes(256-len(rec));frames+=rec
        stats.append({'f':f,'segment':k,'banks':[p[0] for p in poses]})
    banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384));assert len(banks)==64
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
    (OUT/'VECTOR_RUSH.ROM').write_bytes(rom)
    report={'frames':N,'rom_bytes':len(rom),'chunks':[{'v':len(m.v),'f':len(m.f)} for m,o in chunks],'sha256':hashlib.sha256(rom).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
