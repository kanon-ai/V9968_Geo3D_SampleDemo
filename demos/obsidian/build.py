import os
"""Original geometry + camera data, assembled into an ASCII16 geo3d ROM.
Only transforms/order/star positions are precomputed. geo3d draws every face.
"""
from pathlib import Path
import math, random, struct, subprocess, json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'out'; OUT.mkdir(exist_ok=True)
TOOL = Path(os.environ['SDCC_BIN']).resolve()
FRAME_COUNT = 512

def words(values):
    return struct.pack('<'+'h'*len(values), *[round(v) for v in values])

class Mesh:
    def __init__(self): self.v=[]; self.f=[]; self.objects=0
    def poly(self, points, normal, base=1):
        start=len(self.v); self.v.extend(points)
        ids=list(range(start,start+len(points)))
        if len(ids)==3: ids.append(ids[-1])
        self.f.append((ids,normal,base))
    def box(self,x,y,z,sx,sy,sz,base=1):
        first=len(self.v); self.objects+=1
        points=[(x+a*sx/2,y+b*sy/2,z+c*sz/2) for a in (-1,1) for b in (-1,1) for c in (-1,1)]
        self.v.extend(points)
        for axis in range(3):
            axes=[k for k in range(3) if k!=axis]
            for side in (0,1):
                n=[0,0,0]; n[axis]=2*side-1
                ids=[]
                for u,v in ((0,0),(1,0),(1,1),(0,1)):
                    bits=[0,0,0]; bits[axis]=side;bits[axes[0]]=u;bits[axes[1]]=v
                    ids.append(bits[0]*4+bits[1]*2+bits[2])
                p=np.array([points[j] for j in ids])
                if np.dot(np.cross(p[1]-p[0],p[2]-p[0]),n)<0: ids.reverse()
                self.f.append(([first+j for j in ids],n,base))
    def hull(self,z0,z1,w0,w1):
        first=len(self.v); self.objects+=1
        ring=[(-1,0),(-.78,85),(.78,85),(1,0),(.75,-125),(.4,-185),(-.4,-185),(-.75,-125)]
        for z,w in ((z0,w0),(z1,w1)):
            self.v.extend([(x*w,y,z) for x,y in ring])
        for i in range(8):
            ids=[first+i,first+(i+1)%8,first+8+(i+1)%8,first+8+i]
            p=np.array([self.v[j] for j in ids]);n=np.cross(p[1]-p[0],p[2]-p[0]);n=n/np.linalg.norm(n)
            center=p.mean(axis=0)-np.array([0,-35,(z0+z1)/2])
            if np.dot(n,center)<0: ids.reverse();n=-n
            self.f.append((ids,n.tolist(),1))
        # End caps as triangle fans, shared vertices.
        for start,normal in ((first,[0,0,-1]),(first+8,[0,0,1])):
            for i in range(1,7):
                ids=[start,start+i,start+i+1,start+i+1]
                p=np.array([self.v[j] for j in ids])
                if np.dot(np.cross(p[1]-p[0],p[2]-p[0]),normal)<0: ids.reverse()
                self.f.append((ids,normal,1))
    def data(self):
        assert len(self.v)<=255 and len(self.f)<=255,(len(self.v),len(self.f))
        vb=b''.join(words(v) for v in self.v)
        fb=b''.join(bytes(ids)+words([n*16384 for n in normal])+bytes([base]) for ids,normal,base in self.f)
        return bytes([len(self.v),len(self.f)])+struct.pack('<HH',len(vb),len(fb))+vb+fb

def make_models():
    rng=random.Random(831); result=[]
    widths=[85,290,380,430,440,420,370,320,290]
    for i in range(8):
        m=Mesh();z=-1750+i*500;w=(widths[i]+widths[i+1])/2
        m.hull(z-250,z+250,widths[i],widths[i+1])
        # Deck modules: staggered heights make the flyby readable in silhouette.
        for row in range(3):
            for col in range(3):
                h=rng.randint(35,125)+(150 if i in (3,4) and col==1 else 0)
                m.box((col-1)*w*.43,85+h/2,z+(row-1)*145,w*.30,h,112,8 if col==1 and row==1 else 1)
        # Outboard armor pods and their illuminated service apertures.
        for side in (-1,1):
            for row in range(3):
                zz=z+(row-1)*150
                m.box(side*(w+35),-15,zz,86,64,110)
                xx=side*(w+79)
                pts=[(xx,-10,zz-30),(xx,8,zz-30),(xx,8,zz+30),(xx,-10,zz+30)]
                if side<0:pts.reverse()
                m.poly(pts,[0,0,0],14)
        # Longitudinal deck conduits and two turret barrels.
        for side in (-1,1):
            m.box(side*w*.76,104,z,18,24,450,8)
            m.box(side*w*.48,175,z-90,26,30,190,1)
        # A high antenna and a heavy crosspiece on alternate sections.
        m.box(0,310 if i in (3,4) else 210,z+80,16,190,16,8)
        m.box(0,365 if i in (3,4) else 265,z+80,110,14,14,1)
        # Escort silhouette: delta wings, nose, dorsal spine, exhaust.
        ex=650+80*math.sin(i);ey=100+70*math.cos(i);ez=z-180
        m.poly([(ex-85,ey,ez+85),(ex+85,ey,ez+85),(ex,ey+14,ez-120)],[0,1,0],8)
        m.poly([(ex-85,ey,ez+85),(ex,ey-18,ez-90),(ex+85,ey,ez+85)],[0,-1,0],1)
        m.box(ex,ey+12,ez,24,24,115,1)
        m.poly([(ex-18,ey-4,ez+70),(ex+18,ey-4,ez+70),(ex,ey+12,ez+190)],[0,0,0],15)
        assert len(m.v)<=255
        result.append(m)
    return result

CAM=np.array([[1500,900,-3600],[900,430,-1800],[700,450,-350],[800,650,1650],[1300,1000,3000],[-1500,1300,1000],[-1400,850,-1900],[1500,900,-3600]],float)
TARGET=np.array([[0,0,0],[0,0,0],[0,100,850],[0,100,850],[0,0,300],[0,0,0],[0,0,-300],[0,0,0]],float)
def spline(table,t):
    u=t*(len(table)-1);i=min(int(u),len(table)-2);f=u-i
    p0=table[max(0,i-1)];p1=table[i];p2=table[i+1];p3=table[min(len(table)-1,i+2)]
    return .5*((2*p1)+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f*f*f)
def camera(t):
    eye=spline(CAM,t); target=spline(TARGET,t)
    f=target-eye;f/=np.linalg.norm(f)
    r=np.cross([0,1,0],f);r/=np.linalg.norm(r);u=np.cross(f,r)
    roll=.10*math.sin(t*math.tau*3)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    mat=np.array([rr,uu,f]);return mat,-mat@eye,eye

COLORS=[(2,4,12),(10,20,36),(24,40,62),(43,65,88),(68,94,117),(104,137,157),(151,186,200),(211,238,246),
        (35,14,12),(68,27,16),(104,45,22),(150,69,29),(197,102,41),(241,151,69),(255,215,115),(255,255,255)]
def background():
    im=Image.new('P',(256,212));im.putpalette(sum([list(c) for c in COLORS],[])+[0]*(768-48))
    d=ImageDraw.Draw(im); rng=random.Random(919)
    for _ in range(350):
        x=rng.randrange(256);y=rng.randrange(16,196)
        if rng.random()<.20: d.point((x,y),1)
    font=ImageFont.truetype(os.environ['ROM_FONT'],10)
    d.rectangle((0,0,255,14),fill=0);d.line((5,14,250,14),fill=3)
    d.text((6,1),'OBSIDIAN // TITAN PASS',font=font,fill=7)
    d.rectangle((0,197,255,211),fill=0);d.line((5,197,250,197),fill=3)
    d.text((6,199),'GEO3D  /  LIVE POLYGON FLIGHT',font=font,fill=6)
    im.save(OUT/'atlas.png')
    arr=np.array(im,dtype=np.uint8)
    return bytes(((arr[:,::2]<<4)|arr[:,1::2]).flat)

def build():
    models=make_models(); banks=[bytearray(16384)]
    for m in models:
        data=m.data();banks.append(bytearray(data+bytes(16384-len(data))))
    bg=background();banks += [bytearray(bg[:16384]),bytearray(bg[16384:]+bytes(32768-len(bg)))]
    rng=np.random.default_rng(43);stars=rng.normal(size=(600,3));stars/=np.linalg.norm(stars,axis=1)[:,None]
    frames=bytearray()
    for frame in range(FRAME_COUNT):
        t=frame/FRAME_COUNT;mat,trans,eye=camera(t)
        data=bytearray(words((mat*16384).flatten().tolist()+trans.tolist()))
        light=mat@np.array([-.35,.7,-.62]);light/=np.linalg.norm(light)
        data+=words(light*16384)
        order=sorted(range(8),key=lambda i:(mat@np.array([0,0,-1750+500*i])+trans)[2],reverse=True)
        data+=bytes(i+1 for i in order)
        points=[]
        for index,s in enumerate(stars):
            v=mat@s
            if v[2]>.1:
                x=round(128+158*v[0]/v[2]);y=round(106-158*v[1]/v[2])
                if 2<=x<253 and 16<=y<196:points.append((x&254,y,[0x33,0x55,0x77,0xFF][index%4]))
            if len(points)==24:break
        points += [(0,0,0)]*(24-len(points))
        data+=bytes(v for p in points for v in p)
        roll=.22*math.sin(t*math.tau*3);cr=math.cos(roll);sr=math.sin(roll)
        data+=words(np.array([[cr,-sr,0],[sr,cr,0],[0,0,1]]).flatten()*16384)
        assert len(data)==128
        frames+=data
    banks += [frames[i:i+16384] for i in range(0,len(frames),16384)]
    pal=[]
    for r,g,b in COLORS:
        r,g,b=[round(v/255*7) for v in (r,g,b)];pal += [(r<<4)|b,g]
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(str(v) for v in pal)+'\n')
    subprocess.run([str(TOOL/'sdasz80.exe'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],check=True,cwd=ROOT/'src')
    subprocess.run([str(TOOL/'sdldz80.exe'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],check=True,cwd=ROOT)
    for line in (OUT/'player.ihx').read_text().splitlines():
        record=bytes.fromhex(line[1:]);n=record[0];addr=int.from_bytes(record[1:3],'big');typ=record[3]
        assert sum(record)%256==0
        if typ==0:
            if addr>=0xE800:
                assert addr+n<=0xF200
                addr=addr-0xE800+0x4100
            assert 0x4000<=addr and addr+n<=0x8000
            banks[0][addr-0x4000:addr-0x4000+n]=record[4:4+n]
    # Original third-person scout. Nose is towards +Z, away from the viewer.
    scout=Mesh()
    scout.v=[(0,0,70),(-47,-4,-25),(47,-4,-25),(0,13,-12),(0,-9,-18),(-13,0,-35),(13,0,-35),(0,18,-32)]
    for ids,base in (([0,1,3],1),([0,3,2],1),([0,4,1],1),([0,2,4],1),([1,5,3],8),([2,3,6],8),([3,5,7],1),([3,7,6],1),([5,6,7],8),([5,1,4],1),([6,4,2],1),([5,4,6],1)):
        p=np.array([scout.v[j] for j in ids],float); n=np.cross(p[1]-p[0],p[2]-p[0]); n/=np.linalg.norm(n)
        center=p.mean(axis=0)-np.array([0,0,-6])
        if np.dot(n,center)<0:ids=ids[::-1];n=-n
        scout.f.append((ids+[ids[-1]],n.tolist(),base))
    for side in (-1,1):
        x=side*10
        scout.poly([(x-4,-2,-37),(x+4,-2,-37),(x+4,4,-37),(x-4,4,-37)],[0,0,0],15)
    sd=scout.data();assert len(scout.v)==16 and len(scout.f)==14
    banks.append(bytearray(sd+bytes(16384-len(sd))))
    assert len(banks)==16
    rom=b''.join(banks);assert len(rom)==262144
    (OUT/'OBSIDIAN_GEO3D.ROM').write_bytes(rom)
    stats={'solid_components':sum(m.objects for m in models),'escort_craft':8,'player_craft':1,'vertices':sum(len(m.v) for m in models)+len(scout.v),'faces':sum(len(m.f) for m in models)+len(scout.f),'batches':9,'per_world_batch':[(len(m.v),len(m.f)) for m in models],'geometry_ram_bytes':sum(len(m.data())-6 for m in models),'frames':512,'rom_bytes':len(rom),'sha256':hashlib.sha256(rom).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))

if __name__=='__main__':build()
