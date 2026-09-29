import os
from pathlib import Path
import math,struct,json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from mesh import Mesh,words
from hudfont import label
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
TOOL=Path(os.environ['SDCC_BIN']).resolve()
N=1536
# Quantized V9938 palette: ocean blues, land, desert, lunar neutral grays.
COLORS=[(0,0,0),(0,0,36),(0,36,73),(0,73,146),(36,109,182),(73,146,219),(36,73,36),(73,109,36),(146,146,73),(182,146,109),(36,36,36),(73,73,73),(109,109,109),(146,146,146),(182,182,182),(255,255,255)]
def bitmap(im):
 a=np.array(im,dtype=np.uint8);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def sphere(radius,nlon,nlat,vbase,flip_u=False):
 m=Mesh();uv=[]
 m.v=[(0,radius,0)]
 for j in range(1,nlat):
  t=math.pi*j/nlat
  for i in range(nlon):
   a=2*math.pi*i/nlon;m.v.append((radius*math.sin(t)*math.sin(a),radius*math.cos(t),radius*math.sin(t)*math.cos(a)))
 south=len(m.v);m.v.append((0,-radius,0))
 def vi(j,i):return 0 if j==0 else south if j==nlat else 1+(j-1)*nlon+i%nlon
 for j in range(nlat):
  for i in range(nlon):
   ids=[vi(j,i),vi(j+1,i),vi(j+1,i+1),vi(j,i+1)]
   coords=[(round(i*255/nlon),vbase+round(j*63/nlat)),(round(i*255/nlon),vbase+round((j+1)*63/nlat)),(round((i+1)*255/nlon),vbase+round((j+1)*63/nlat)),(round((i+1)*255/nlon),vbase+round(j*63/nlat))]
   # Match eastward map longitude to the outward-facing sphere.
   if flip_u:coords=[(255-u,v) for u,v in coords]
   # Collapse polar quads to valid triangles, keeping UV corners attached.
   if j==0:ids=ids[1:]+[ids[1]];coords=coords[1:]+[coords[1]]
   if j==nlat-1:ids=[ids[0],ids[1],ids[3],ids[3]];coords=[coords[0],coords[1],coords[3],coords[3]]
   pts=np.array([m.v[k] for k in ids]);normal=pts.mean(axis=0);normal/=np.linalg.norm(normal)
   if np.dot(np.cross(pts[1]-pts[0],pts[2]-pts[0]),normal)<0:
    ids=[ids[2],ids[1],ids[0],ids[0] if len(set(ids))==3 else ids[3]]
    coords=[coords[2],coords[1],coords[0],coords[0] if len(set(ids))==3 else coords[3]]
   m.f.append((ids,normal.tolist(),128));uv.extend(v for q in coords for v in q)
 d=m.data()+bytes(uv);assert len(d)<16384
 return bytearray(d+bytes(16384-len(d))),{'vertices':len(m.v),'faces':len(m.f)}
def distant_ufo():
 m=Mesh();rings=[(2,65),(30,60),(44,28),(100,0),(100,-10),(30,-22)]
 n=12
 for radius,y in rings:
  for i in range(n):
   t=2*math.pi*i/n;m.v.append((radius*math.sin(t),y,radius*math.cos(t)))
 for j in range(len(rings)-1):
  for i in range(n):
   ids=[j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n]
   pts=np.array([m.v[k] for k in ids]);normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);normal/=np.linalg.norm(normal)
   if np.dot(normal,pts.mean(axis=0)*np.array([1,0,1]))<0:ids=ids[::-1];normal=-normal
   m.f.append((ids,(normal*.65).tolist(),10))
 for i in range(3):
  t=i*2*math.pi/3;m.box(50*math.sin(t),-28,50*math.cos(t),18,20,18,10)
 # Fixed grayscale on the tiny landing pods; no extra texture image.
 for i in range(60,len(m.f)):
  ids,normal,base=m.f[i];m.f[i]=(ids,[0,0,0],12)
 d=m.data()+bytes(len(m.f)*8)
 return bytearray(d+bytes(16384-len(d))),{'vertices':len(m.v),'faces':len(m.f)}

def ry(a):return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def rz(a):return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def build():
 banks=[bytearray(16384) for _ in range(40)]
 banks[1],earth=sphere(165,20,12,0,flip_u=True);banks[2],moon=sphere(46,16,10,64)
 banks[3],ufo=distant_ufo()
 meshstats={'earth':earth,'moon':moon,'distant_ufo':ufo}
 pal=sum([list(c) for c in COLORS],[])+[0]*720
 sky=Image.new('P',(256,256));sky.putpalette(pal);d=ImageDraw.Draw(sky)
 rng=np.random.default_rng(12)
 for x,y in rng.integers(0,256,(55,2)):d.point((int(x),int(y)),fill=12 if x%3 else 14)
 sky.save(OUT/'sky.png');bb=bitmap(sky);banks[4]=bytearray(bb[:16384]);banks[5]=bytearray(bb[16384:])
 hud=Image.new('P',(256,256));hud.putpalette(pal);d=ImageDraw.Draw(hud)
 label(d,(7,0),'ORBITAL / V9968+GEO3D',fill=14)
 label(d,(15,16),'EARTH + MOON / TEXTURE',fill=13)
 hud.save(OUT/'hud.png');bb=bitmap(hud);banks[6]=bytearray(bb[:16384]);banks[7]=bytearray(bb[16384:])
 source=Image.open(ROOT/'assets/planet-atlas-generated.png').convert('RGB').resize((256,128),Image.Resampling.LANCZOS)
 arr=np.asarray(source,dtype=np.float32);palette=np.array(COLORS,dtype=np.float32)
 # Seven pre-shaded VRAM copies; Geo3D normal lighting selects the copy.
 texture=bytearray()
 for level in range(7):
  rgb=arr*(.22+.78*level/6)
  ids=np.argmin(np.sum((rgb[:,:,None,:]-palette[None,None,:,:])**2,axis=3),axis=2).astype(np.uint8)
  im=Image.fromarray(ids).convert('P');im.putpalette(pal)
  im.save(OUT/f'texture-level-{level}.png');texture+=bitmap(im)
 assert len(texture)==7*16384
 for i in range(7):banks[8+i]=texture[i*16384:(i+1)*16384]
 frames=bytearray()
 for f in range(N):
  t=2*math.pi*f/N
  earthpose=(1,rz(-.20)@ry(t),np.array([0,0,580]))
  moonpos=np.array([290*math.cos(t),65*math.sin(t),580+250*math.sin(t)])
  # Keep the same local +Z hemisphere facing Earth along the existing inclined orbit.
  facing=earthpose[2]-moonpos;facing/=np.linalg.norm(facing)
  orbit_up=np.array([0.,250.,-65.]);orbit_up/=np.linalg.norm(orbit_up)
  right=np.cross(orbit_up,facing);right/=np.linalg.norm(right)
  moonpose=(2,np.column_stack((right,np.cross(facing,right),facing)),moonpos)
  # One small background cameo per cycle, never in front of either planet.
  u=(f-720)/240
  ufopose=(3 if 0<=u<1 else 255,rz(.12*math.sin(u*12))@np.array([[1,0,0],[0,.955336,.295520],[0,-.295520,.955336]]),np.array([-2400+4800*u,660+35*math.sin(u*9),3600]))
  poses=[ufopose]+sorted([earthpose,moonpose],key=lambda x:x[2][2],reverse=True)
  poses += [(255,np.eye(3),np.array([0,0,2000]))]*4
  rec=bytearray()
  for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
  rec+=bytes([x[0] for x in poses])+bytes(1)
  rec+=words([0,512,256,0])+struct.pack('<HH',768,784)
  rec+=bytes(256-len(rec));frames+=rec
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
 (OUT/'ORBITAL.ROM').write_bytes(rom)
 report={'frames':N,'rom_bytes':len(rom),'meshes':meshstats,'sha256':hashlib.sha256(rom).hexdigest()}
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
