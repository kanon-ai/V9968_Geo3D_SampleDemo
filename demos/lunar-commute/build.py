from pathlib import Path
import math,struct,subprocess,json,hashlib,os,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from models import Model,cat,rabbit,rocket
from mesh import words
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True);N=600
found=shutil.which('sdasz80') or shutil.which('sdasz80.exe')
T=Path(os.environ['SDCC_BIN']) if 'SDCC_BIN' in os.environ else Path(found).parent if found else None
if T is None:raise SystemExit('Set SDCC_BIN to the SDCC bin directory.')
EXE='.exe' if os.name=='nt' else ''
def ry(a):return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def rx(a):return np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
def rz(a):return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def ease(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def mix(a,b,t):return np.array(a)*(1-t)+np.array(b)*t
base=[(0,0,0),(8,12,30),(15,38,74),(25,81,145),(49,139,202),(110,192,222),(43,85,87),(204,64,58),(239,164,63),(255,221,143),(110,67,35),(247,148,154),(101,110,119),(232,218,192),(203,225,237),(255,249,225)]
sheet=Image.open(P/'assets/space-regolith.png').convert('RGB');w,h=sheet.size
sky=sheet.crop((0,0,w,h//2)).resize((256,212),Image.Resampling.LANCZOS)
# Long-exposure-like sky is deliberately restrained; no planets baked into it.
sky=Image.fromarray(np.uint8(np.asarray(sky)*.52))
reg=Image.open(P/'assets/lunar-soft-tile.png').convert('RGB').resize((128,128),Image.Resampling.LANCZOS)
faces=Image.open(P/'assets/character-faces.png').convert('RGB').resize((128,64),Image.Resampling.LANCZOS)
earth=Image.open(P/'assets/earth-clouds-nasa.jpg').convert('RGB').resize((256,128),Image.Resampling.LANCZOS)
# Equirectangular convention: left=-180deg, right=+180deg, north at top.
lon=np.linspace(-math.pi,math.pi,256)[None,:];lat=np.linspace(math.pi/2,-math.pi/2,128)[:,None]
yaw=math.radians(-4);earth_rotation=rx(math.radians(-40))@ry(yaw)
normal=np.stack(np.broadcast_arrays(np.cos(lat)*np.sin(lon),np.sin(lat),-np.cos(lat)*np.cos(lon)),axis=2)@earth_rotation.T
light=np.array([-.4,.5,-.77]);light/=np.linalg.norm(light);diff=np.maximum(0,normal@light)
rgb=np.asarray(earth).astype(float)*(.065+.935*diff[:,:,None]**.65);earth=Image.fromarray(np.uint8(np.clip(rgb,0,255)))
atlas=Image.new('RGB',(256,256));atlas.paste(earth,(0,0));atlas.paste(reg,(0,128));atlas.paste(faces,(128,128))
samples=Image.new('RGB',(256,512));samples.paste(atlas,(0,0));samples.paste(sky,(0,256));extra=samples.quantize(colors=240,method=Image.Quantize.MEDIANCUT).getpalette()[:720]
colors=base+[tuple(extra[i:i+3]) for i in range(0,720,3)];pal=Image.new('P',(1,1));pal.putpalette(sum(map(list,colors),[]))
def quant(im):return im.quantize(palette=pal,dither=Image.Dither.NONE)
sky=quant(sky);atlas=quant(atlas);sky.save(O/'sky.png');atlas.save(O/'atlas.png')
banks=[bytearray(16384) for _ in range(64)];bg=Image.new('P',(256,256),1);bg.putpalette(pal.getpalette());bg.paste(sky);raw=bg.tobytes()
for i in range(4):banks[4+i][:]=raw[i*16384:(i+1)*16384]
raw=atlas.tobytes()
for i in range(4):banks[24+i][:]=raw[i*16384:(i+1)*16384]
stats={};source_models={}
def save(bank,m):
 source_models[bank]=m
 banks[bank],stats[str(bank)]=m.pack()
def textured(m,pts,uv):
 i=len(m.f);m.polygon(pts,128);m.uv=getattr(m,'uv',{});m.uv[i]=sum(([u,v] for u,v in uv),[])
# A true sphere; shared poles/vertices and per-face longitude UVs preserve seam direction.
m=Model();nl=20;nt=12
for j in range(nt+1):
 lat0=math.pi/2-j*math.pi/nt
 for i in range(nl+1):
  lo=-math.pi+i*2*math.pi/nl;m.v.append((500*math.cos(lat0)*math.sin(lo),500*math.sin(lat0),-500*math.cos(lat0)*math.cos(lo)))
# weld poles and longitude seam to stay within Geo3D's 255-vertex limit
old=m.v;m.v=[];remap=[];lookup={}
for v in old:
 k=tuple(round(x,5) for x in v)
 if k not in lookup:lookup[k]=len(m.v);m.v.append(v)
 remap.append(lookup[k])
m.uv={}
for j in range(nt):
 for i in range(nl):
  ids=[remap[j*(nl+1)+i],remap[(j+1)*(nl+1)+i],remap[(j+1)*(nl+1)+i+1],remap[j*(nl+1)+i+1]];uv=[(round(i*255/nl),round(j*127/nt)),(round(i*255/nl),round((j+1)*127/nt)),(round((i+1)*255/nl),round((j+1)*127/nt)),(round((i+1)*255/nl),round(j*127/nt))]
  if j==0:ids=ids[1:]+[ids[1]];uv=uv[1:]+[uv[1]]
  if j==nt-1:ids=[ids[0],ids[1],ids[3],ids[3]];uv=[uv[0],uv[1],uv[3],uv[3]]
  a=np.array([m.v[k] for k in ids]);n=np.cross(a[1]-a[0],a[2]-a[0]);
  if np.dot(n,a.mean(axis=0))<0:ids=ids[::-1];uv=uv[::-1]
  # Discard permanently hidden hemisphere; Earth orientation is fixed in this short scene.
  if (earth_rotation@a.mean(axis=0))[2]>45:continue
  m.face(ids,128);m.uv[len(m.f)-1]=sum(([u,v] for u,v in uv),[])
save(1,m)
# Low ridge conceals the Earth at the start; camera rises, Earth stays fixed.
def lunar_height(x,z):
 ridge=(330+12*math.sin(x*.002))*math.exp(-((z-6500)/2100)**2)
 r=math.sqrt((x-180)**2+(z-3000)**2)
 crater=22*math.exp(-((r-570)/130)**2)-14*math.exp(-(r/440)**4)
 return ridge+crater
for bank,z0,z1 in [(2,4200,11000),(3,1700,4200),(8,400,1700),(9,90,400)]:
 m=Model();m.uv={};zs=np.geomspace(z0,z1,7);xs=np.linspace(-.18,.48,9)
 if bank in (8,9):zs=np.linspace(-1200 if bank==9 else 100,100 if bank==9 else 1700,13)
 for z in zs:
  for i,a in enumerate(xs):
   x=(-1000+i*250) if bank in (8,9) else a*z
   m.v.append((x,lunar_height(x,z),z))
 for j in range(len(zs)-2,-1,-1):
  for i in range(8):
   ids=[j*9+i,j*9+i+1,(j+1)*9+i+1,(j+1)*9+i]
   uv=[(16,144),(111,144),(111,239),(16,239)]
   for tri in [(0,3,2),(0,2,1)]:
    corners=[ids[k] for k in tri];m.face(corners,128);coords=[uv[k] for k in tri];coords.append(coords[-1]);m.uv[len(m.f)-1]=sum(([u,v] for u,v in coords),[])
 save(bank,m)
for who,bank0 in [('cat',16),('rabbit',20)]:
 for k in range(4):
  m=cat() if who=='cat' else rabbit()
  if who=='rabbit':
   m.orb(-10,2,-4,9,6,13,15,n=4,lat=2);m.orb(10,2,-4,9,6,13,15,n=4,lat=2)
  # Moving feet with a low-gravity step; body bob is animated separately.
  for i,(x,y,z) in enumerate(m.v):
   if y<13 and z<15:m.v[i]=(x,y+max(0,math.sin(k*math.pi/2+(0 if x<0 else math.pi)))*9,z+math.sin(k*math.pi/2+(0 if x<0 else math.pi))*12)
  for i,uv in getattr(m,'uv',{}).items():m.uv[i]=[v+128 if n%2 else v for n,v in enumerate(uv)]
  save(bank0+k,m)
save(15,rocket())
# Conservative offline visibility pruning: no visible face or UV is modified.
variant_cache={};free_banks=[10,11,12,13,14]+list(range(28,40))+list(range(60,64));pool_index=0;pool_offset=0
def compact(bank,mat,pos):
 global pool_index,pool_offset
 if bank==255:return 255,0x4000
 if bank not in [1,2,3,8,9]:return bank,0x4000
 model=source_models[bank];v=np.asarray(model.v)@mat.T+np.asarray(pos);keep=[]
 for i,(ids,n,c) in enumerate(model.f):
  pts=v[ids]
  if np.any(pts[:,2]<=4):keep.append(i);continue
  xx=128+1400*pts[:,0]/pts[:,2];yy=106-1400*pts[:,1]/pts[:,2]
  if xx.max()<-16 or xx.min()>272 or yy.max()<-16 or yy.min()>228:continue
  keep.append(i)
 if not keep:return 255,0x4000
 key=(bank,tuple(keep))
 if key in variant_cache:return variant_cache[key]
 m=Model();m.uv={};remap={}
 for i in keep:
  ids,n,c=model.f[i];new=[]
  for old in ids:
   if old not in remap:remap[old]=len(m.v);m.v.append(model.v[old])
   new.append(remap[old])
  m.f.append((new,n,c))
  if i in model.uv:m.uv[len(m.f)-1]=model.uv[i]
 raw=m.pack()[0];size=6+len(m.v)*6+len(m.f)*19;size=(size+15)//16*16
 if pool_offset+size>16384:pool_index+=1;pool_offset=0
 assert pool_index<len(free_banks), 'visibility variants exceed ROM pool'
 dest=free_banks[pool_index];address=0x4000+pool_offset;banks[dest][pool_offset:pool_offset+size]=raw[:size];pool_offset+=size
 variant_cache[key]=(dest,address);return dest,address
frames=bytearray();motion=[]
for output_frame in range(N):
 f=float(np.interp(output_frame,[0,108,132,600],[0,250,250,1024]))
 cam=150+85*ease(f/250)
 walku=ease((f-275)/425);cx=-600+1650*walku
 pan=.30*ease((f-410)/300)*(1-ease((f-850)/140));view=rx(.055*(1-ease(f/250)))@ry(-pan)
 poses=[(1,view@earth_rotation,view@np.array([0,1000-cam,30000])),(2,view,view@np.array([0,-cam,0])),(3,view,view@np.array([0,-cam,0])),(8 if f<250 else 255,view,view@np.array([0,-cam,0])),(9 if f<250 else 255,view,view@np.array([0,-cam,0]))]
 def ground(x,z):return lunar_height(x,z)
 cbank=rbank=255;cbob=rbob=0
 if f>=275:
  walking=f<700;cbank=16+(int(f//5)%4 if walking else 0);rbank=20+(int(f//5)%4 if walking else 0)
  if walking:cbob=abs(math.sin(f*.18))*7;rbob=abs(math.sin(f*.18+1))*7
 cpos=np.array([cx,ground(cx,3400)+cbob,3400]);rpos=np.array([cx-100,ground(cx-100,3500)+rbob,3500]);cr=-.9 if f<700 else 0
 sp=np.array([1220.,ground(1220,3450)+62,3450]);shipmat=np.eye(3);charscale=1.
 if f>=710:
  u=ease((f-710)/110);charscale=1-.35*u;cpos=mix([1050,ground(1050,3400),3400],sp+[-40,18,0],u);rpos=mix([950,ground(950,3500),3500],sp+[35,18,0],u)
  cpos[1]+=math.sin(u*math.pi)*45;rpos[1]+=math.sin(u*math.pi)*55
 if f>=820:
  u=ease((f-820)/180);sp=mix([1220,ground(1220,3450)+62,3450],[0,1000,28000],u);shipmat=ry(math.pi/2*ease(u*3))@rz(-.20*math.sin(u*math.pi));cpos=sp+shipmat@np.array([-40,18,0]);rpos=sp+shipmat@np.array([35,18,0]);charscale=.65
 poses.extend([(15,view@shipmat,view@(sp-[0,cam,0])),(cbank,view@(shipmat if f>=820 else ry(cr))*charscale,view@(cpos-[0,cam,0])),(rbank,view@(shipmat if f>=820 else ry(cr))*charscale,view@(rpos-[0,cam,0]))])
 if f>=820:
  follow=ease((f-820)/180)
  camera_delta=view@np.array([0,765*follow,20000*follow])
  poses=[(bank,mat,pos-camera_delta) for bank,mat,pos in poses]
  # Terrain wholly behind the tracking camera must not cross the near plane.
  for i in (1,2,3,4):
   bank,mat,pos=poses[i]
   if bank!=255 and max((np.asarray(source_models[bank].v)@mat.T+pos)[:,2])<4:poses[i]=(255,mat,pos)
 for i in [0,5,6,7]:
  bank,mat,pos=poses[i];radius=500 if i==0 else 190 if i==5 else 90
  if pos[2]>0 and abs(1400*pos[0]/pos[2])>128+1400*radius/pos[2]:poses[i]=(255,mat,pos)
 # Lunar horizon rolls down during the opening; Earth remains fixed.
 tilt=rx(-.032*(1-ease(f/250)))
 poses=[(bank,view@tilt if bank in (2,3,8,9) else mat,pos) for bank,mat,pos in poses]
 # Opening camera advances toward the ridge; later choreography is unchanged.
 advance=1200*(1-ease(f/250))
 poses=[(bank,mat,pos+view@np.array([0,0,advance])) for bank,mat,pos in poses]
 addresses=[];newposes=[]
 for bank,mat,pos in poses:
  resource,address=compact(bank,mat,pos);addresses.append(address);newposes.append((resource,mat,pos))
 poses=newposes
 rec=bytearray()
 for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+list(pos))
 rec+=bytes([x[0] for x in poses]);rec+=struct.pack('<H',round(pan*1400)%256);rec+=struct.pack('<8H',*addresses);rec+=bytes(256-len(rec));frames+=rec
 motion.append({'f':output_frame,'story_frame':f,'camera_y':float(cam),'camera_pan':float(pan),'earth_angular_diameter_degrees':math.degrees(2*math.atan(500/30000)),'phase':'reveal' if f<275 else 'walk' if f<710 else 'board' if f<820 else 'home'})
for i in range((len(frames)+16383)//16384):banks[40+i][:len(frames[i*16384:(i+1)*16384])]=frames[i*16384:(i+1)*16384]
paldata=[round(c/255*31) for rgb in colors for c in rgb];(P/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,paldata))+'\n')
subprocess.run([str(T/('sdasz80'+EXE)),'-los',str(O/'player.rel'),str(P/'src/player.asm')],cwd=P/'src',check=True);subprocess.run([str(T/('sdldz80'+EXE)),'-n','-i',str(O/'player'),str(O/'player.rel')],cwd=P,check=True)
for line in (O/'player.ihx').read_text().splitlines():
 r=bytes.fromhex(line[1:]);assert sum(r)%256==0
 if r[3]==0:
  n=r[0];a=int.from_bytes(r[1:3],'big')
  if a>=0xD000:assert a+n<=0xE000;a=a-0xD000+0x4100
  banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
rom=b''.join(banks);assert len(rom)==1048576;(O/'EARTHRISE-HOME.ROM').write_bytes(rom)
report={'frames':N,'rom_bytes':len(rom),'sha256':hashlib.sha256(rom).hexdigest(),'models':stats,'mode':'SCREEN8 EPAL 256 colors'};(O/'build.json').write_text(json.dumps(report,indent=2));(O/'motion.json').write_text(json.dumps(motion));print(report)


