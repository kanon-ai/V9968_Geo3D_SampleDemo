from pathlib import Path
import math,struct,json,subprocess,hashlib,os,shutil
import numpy as np
from PIL import Image,ImageDraw
from mesh import Mesh,words
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
def tool(name):
    directory=os.environ.get('SDCC_BIN')
    if directory:
        candidate=Path(directory)/(name+'.exe' if os.name=='nt' else name)
        if candidate.is_file():return str(candidate)
    found=shutil.which(name)
    if not found:raise RuntimeError('Install SDCC and add its bin directory to PATH or set SDCC_BIN: '+name)
    return found
N=1536
GROUPS=int(os.environ.get('PETAL_GROUPS','7'))
COLORS=[(0,0,0),(109,0,36),(182,36,73),(255,109,182),(255,182,219),(255,255,255),(0,36,0),(73,146,0),(219,255,73),(109,0,0),(182,0,0),(255,73,0),(255,182,36),(73,109,146),(146,182,219),(219,255,255)]
def ry(a):return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def rx(a):return np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
def rz(a):return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def bitmap(a):return bytes(((a[:,::2]<<4)|a[:,1::2]).astype(np.uint8).flat)
def foliage(season,phase):
 m=Mesh();uv=[];rng=np.random.default_rng(441+season*113)
 count=[18,48,6,18][season]
 for j in range(count):
  size=rng.uniform(*[(16,35),(3,8),(36,66),(8,24)][season])
  center=np.array([rng.uniform(-360,360),rng.uniform(-250,250),rng.uniform(-95,95)])
  a=rng.uniform(0,6.28);mat=rz(a+.35*math.sin(phase+a))@ry(rng.uniform(-2,2)+.55*math.sin(phase+a))@rx(.4*math.cos(phase+a))
  if season==2:
   outline=[(0,-1),(.17,-.47),(.58,-.8),(.47,-.28),(1,-.38),(.65,.10),(.85,.28),(.32,.38),(.10,.62),(.03,1),(-.03,1),(-.10,.62),(-.32,.38),(-.85,.28),(-.65,.10),(-1,-.38),(-.47,-.28),(-.58,-.8),(-.17,-.47)]
   pts=[(0,0)]+outline;tri=[(0,1+k,1+(k+1)%len(outline)) for k in range(len(outline))]
  elif season==0:
   pts=[(-.65,.55),(-.72,-.15),(-.32,-.92),(0,-.68),(.38,-.92),(.72,-.1),(.42,.65)]
   tri=[(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,6)]
  elif season==1:
   pts=[(0,-1),(1,0),(0,1),(-1,0)];tri=[(0,1,2),(0,2,3)]
   size*=.55+.45*(1+math.sin(phase+j))/2
  else:
   # Three crossing slender crystal arms, six tips, no opaque rectangle.
   pts=[];tri=[]
   for k in range(3):
    t=k*math.pi/3;v=np.array([math.cos(t),math.sin(t)]);w=np.array([-v[1],v[0]])*.095
    q=len(pts);pts.extend([tuple(-v-w),tuple(v-w),tuple(v+w),tuple(-v+w)]);tri.extend([(q,q+1,q+2),(q,q+2,q+3)])
  start=len(m.v)
  for x,y in pts:m.v.append(tuple(center+mat@np.array([x*size,y*size,1.5*(x*x-y*y)])))
  for ids in tri:
   for rev in [False,True]:
    ii=list(ids[::-1] if rev else ids);ii.append(ii[-1]);m.f.append(([start+k for k in ii],[0,0,0],128))
    for k in ii:
     x,y=pts[k];uv.extend([season*64+max(0,min(63,int((x+1)*31))),max(0,min(127,int((y+1)*62)))])
 return m.data()+bytes(uv),len(m.v),len(m.f)
def build():
 banks=[bytearray(16384) for _ in range(40)]
 pal=sum([list(c) for c in COLORS],[])+[0]*720
 # Polygon-bounded textures: smooth petal gradients, leaf veins, luminous cores, ice.
 a=np.zeros((128,256),dtype=np.uint8)
 for season in range(4):
  yy,xx=np.mgrid[0:128,0:64];x=(xx-31)/31;y=(yy-63)/63
  if season==0:tile=np.where(np.abs(x)<.28,5,np.where(np.abs(x)<.65,4,3))
  elif season==1:tile=np.where(x*x+y*y<.13,5,np.where(x*x+y*y<.5,8,7))
  elif season==2:
   tile=np.where(y<-.4,12,np.where(np.abs(x)<.48,11,10))
   for k in range(7):
    ang=-math.pi/2+k*2*math.pi/7;dist=np.abs(x*math.sin(ang)-y*math.cos(ang));along=x*math.cos(ang)+y*math.sin(ang)
    tile[(dist<.019)&(along>0)]=12
  else:tile=np.where(x*x+y*y<.4,5,15)
  a[:,season*64:(season+1)*64]=tile
 im=Image.fromarray(a).convert('P');im.putpalette(pal);im.save(OUT/'texture.png')
 for i in range(7):banks[8+i]=bytearray(bitmap(a))
 stats=[]
 cached_topology={}
 for season in range(4):
  for k in range(6):
   data,v,f=foliage(season,k*2*math.pi/6);assert len(data)<16384;banks[15+season*6+k][:len(data)]=data
   # Cache key is valid only when face records and UVs match across all poses.
   topology=data[6+v*6:]
   if season in cached_topology:assert topology==cached_topology[season]
   cached_topology[season]=topology
   banks[15+season*6+k][-1]=season
  stats.append({'season':season,'vertices':v,'faces':f,'per_group':[18,48,6,18][season]})
 frames=bytearray()
 for f in range(N):
  t=2*math.pi*f/N;poses=[]
  for j in range(7):
   # Separate flowing depth layers, with restrained rotational motion.
   a=t*8+j*2*math.pi/7;z=300+j*105+40*math.sin(a)
   mat=rz(.35*math.sin(a)+j*.8)@ry(.25*math.sin(a*.5))
   pos=np.array([170*math.sin(a),((f*3+j*87)%560)-280,z])
   season=((f+j*12)//384)%4
   poses.append((15+season*6+(f//8+j)%6 if j<GROUPS else 255,mat,pos))
  poses.sort(key=lambda x:x[2][2],reverse=True)
  rec=bytearray()
  for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
  rec+=bytes(x[0] for x in poses)+bytes(1);rec+=words([0,512,256,0])+struct.pack('<HH',768,784);rec+=bytes(256-len(rec));frames+=rec
 banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384))
 pal=[]
 for rgb in COLORS:
     r,g,b=[round(c/255*7) for c in rgb];pal.extend([(r<<4)|b,g])
 (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
 subprocess.run([tool('sdasz80'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
 subprocess.run([tool('sdldz80'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
 for line in (OUT/'player.ihx').read_text().splitlines():
     r=bytes.fromhex(line[1:]);assert sum(r)%256==0
     if r[3]==0:
         n=r[0];a=int.from_bytes(r[1:3],'big')
         if a>=0xE800:assert a+n<=0xF000;a=a-0xE800+0x4100
         banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
 rom=b''.join(banks);assert len(rom)==1048576
 (OUT/'PETAL-STORM.ROM').write_bytes(rom)
 report={'frames':N,'rom_bytes':len(rom),'groups':GROUPS,'season_meshes':stats,'sha256':hashlib.sha256(rom).hexdigest()}
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
