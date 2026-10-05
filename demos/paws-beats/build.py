from pathlib import Path
import math,struct,subprocess,json,hashlib,os,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from models import Model,cat,rabbit
from mesh import words
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
found=shutil.which('sdasz80') or shutil.which('sdasz80.exe')
T=Path(os.environ['SDCC_BIN']) if 'SDCC_BIN' in os.environ else Path(found).parent if found else None
if T is None:raise SystemExit('Set SDCC_BIN to the SDCC bin directory or add it to PATH.')
COLORS=[(0,0,0),(0,0,36),(0,36,109),(0,109,182),(73,182,219),(146,219,255),(0,109,109),(219,36,36),(255,146,36),(255,219,73),(109,36,0),(255,109,109),(109,146,182),(255,219,182),(219,255,255),(255,255,255)]
palette=sum(map(list,COLORS),[])+[0]*720
banks=[bytearray(16384) for _ in range(40)]
def image(w,h):
 im=Image.new('P',(w,h),1);im.putpalette(palette);return im

def bitmap(im):
 a=np.array(im,dtype=np.uint8);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def rot(x=0,y=0,z=0):
 c,s=math.cos,math.sin
 return np.array([[c(z),-s(z),0],[s(z),c(z),0],[0,0,1]])@np.array([[c(y),0,s(y)],[0,1,0],[-s(y),0,c(y)]])@np.array([[1,0,0],[0,c(x),-s(x)],[0,s(x),c(x)]])
models={1:cat(),15:rabbit()}
keys=Model()
for j,col in enumerate([7,8,9,6,3,11]):
 x=(j-2.5)*13;keys.cube(x,0,0,11,5,44-j*3,col)
 keys.cube(x,3,-12+j,2,1,2,15)
keys.cube(0,-7,0,87,8,42,10)
for x in [-34,34]:keys.cube(x,-25,0,6,34,6,12);keys.cube(x,-41,0,19,4,24,12)
models[2]=keys
m=Model()
for x,r,col in [(-22,18,3),(22,22,7)]:
 sub=Model();sub.cylinder(-25,0,r,col,10)
 for v in sub.v:m.v.append((v[0]+x,v[1],v[2]))
 off=len(m.v)-len(sub.v)
 for ids,n,c in sub.f:m.f.append(([i+off for i in ids],n,15 if c==14 else c))
 m.cube(x,-38,0,5,26,5,12)
models[16]=m
for bank,paw,head in [(17,13,9),(18,15,15)]:
 m=Model()
 for x in [-21,21]:
  m.orb(x,0,-4,8,8,15,paw,n=6,lat=3)
  # Grip (x,0,-10) to strike tip (x,-20,-36).
  # Tilt only the shaft; preserve tip position and all choreography.
  first=len(m.v)
  m.cube(x,-10,-23,3,math.hypot(20,26),3,10)
  turn=rot(math.atan2(26,20));center=np.array([x,-10,-23])
  for i in range(first,len(m.v)):m.v[i]=tuple(center+turn@(np.array(m.v[i])-center))
  m.orb(x,-20,-36,6,6,6,head,n=6,lat=2)
 models[bank]=m
m=Model()
for x,y,col in [(-60,0,9),(0,16,11),(60,2,5)]:
 m.orb(x,y,0,5,3,2,col,n=6,lat=2);m.cube(x+4,y+8,0,2,16,2,col);m.cube(x+8,y+15,0,9,2,2,col)
models[19]=m
stats={}
for k,m in models.items():banks[k],stats[k]=m.pack()
# Calm little stage, with room for faces and hand movement.
bg=image(256,256);d=ImageDraw.Draw(bg)
for y in range(184):d.line((0,y,255,y),fill=1 if y<100 else 2)
for x in range(12,256,24):
 d.line((x,0,x,11+(x%5)),fill=12);d.ellipse((x-2,12+(x%5),x+2,16+(x%5)),fill=9)
d.rectangle((0,140,255,183),fill=10)
for y in [143,157,177]:d.line((0,y,255,y),fill=8)
for x in [15,65,115,165,215]:d.line((128+(x-128)*.7,140,x,183),fill=8)
raw=bitmap(bg);banks[4][:]=raw[:16384];banks[5][:]=raw[16384:]
hud=image(256,256);d=ImageDraw.Draw(hud);font=ImageFont.truetype(os.environ.get('ROM_FONT','C:/Windows/Fonts/consolab.ttf'),11);small=ImageFont.truetype(os.environ.get('ROM_SMALL_FONT','C:/Windows/Fonts/consola.ttf'),9)
d.text((21,1),'PAWS & BEATS / Geo3D + OPLL',font=small,fill=14)
titles=['ONE, TWO...','CAT ON THE KEYS','BUNNY ON THE DRUMS','LET US PLAY TOGETHER!','THANK YOU!']
for i,title in enumerate(titles):d.text(((256-len(title)*6)//2,16+i*16),title,font=font,fill=9)
raw=bitmap(hud);banks[6][:]=raw[:16384];banks[7][:]=raw[16384:]
# Reuse the same cat/rabbit face artwork as CAT ASCENT.
faces=Image.open(P/'assets/character-faces.png').convert('RGB').resize((128,64),Image.Resampling.LANCZOS)
a=np.asarray(faces,dtype=float);pal=np.array(COLORS,dtype=float)
idx=np.argmin(((a[:,:,None]-pal[None,None])**2).sum(3),axis=2).astype('uint8')
im=Image.fromarray(idx).convert('P');im.putpalette(palette);atlas=image(256,128);atlas.paste(im,(128,0));banks[31][:]=bitmap(atlas);atlas.save(O/'character-atlas.png')
def note(m):
 if m==0:return [0,0]
 hz=440*2**((m-69)/12);b=0
 while hz*72*2**19/3579545/2**b>511:b+=1
 f=round(hz*72*2**19/3579545/2**b);return [f&255,(f>>8)|(b<<1)|16]
# Traditional Ah! vous dirai-je, maman. Zero is the second beat of a long note.
mel=[72,72,79,79,81,81,79,0,77,77,76,76,74,74,72,0,
     79,79,77,77,76,76,74,0,79,79,77,77,76,76,74,0,
     72,72,79,79,81,81,79,0,77,77,76,76,74,74,72,0]
# Transparent LMMM sparkle tiles; no timed trigger is stored in frame data.
spark=image(256,128);spark.paste(0,(0,0,256,128));sd=ImageDraw.Draw(spark)
for tile in range(2):
 for x,y,r in [(5,8,4),(40,5,5),(11,25,3),(36,27,3)]:
  r=max(2,r-tile);x+=tile*48
  sd.polygon([(x,y-r),(x+1,y-1),(x+r,y),(x+1,y+1),(x,y+r),(x-1,y+1),(x-r,y),(x-1,y-1)],fill=9 if tile else 15)
banks[14][:]=bitmap(spark)
frames=bytearray();events=[]
for n in range(640):
 stage=0 if n<64 else 1 if n<192 else 3 if n<576 else 4
 beat=n//8;ph=(n%8)/8
 catplay=stage in [1,3] and mel[(beat-8)%48]!=0;bunplay=stage in [2,3]
 # Each strike coincides with the key-on: contact at phase zero, lift between beats.
 poses=[]
 catpos=np.array([-79.,-73+1.5*math.sin(n*math.pi/4),355.]);bunpos=np.array([79.,-73+1.5*math.cos(n*math.pi/4),355.])
 bow=(math.sin((n-576)/64*math.pi)*.35 if stage==4 else 0)
 cm=rot(bow,.07*math.sin(n*.025),.035*math.sin(n*.08));bm=rot(bow,-.07*math.sin(n*.025),-.035*math.sin(n*.08))
 poses.extend([(1,cm,catpos),(15,bm,bunpos),(2,np.eye(3),np.array([-79.,-50,310.])),(16,np.eye(3),np.array([79.,-50,310.]))])
 for bank,pos,active in [(17,catpos,catplay),(18,bunpos,bunplay)]:
  lift=18*math.sin(ph*math.pi) if active else 16+3*math.sin(n*.08)
  poses.append((bank,rot(.12*math.sin(ph*math.pi) if active else -.2,0,0),pos+np.array([0,43+lift,-20])))
 poses.append((19 if stage==3 else 255,rot(0,0,.08*math.sin(n*.1)),np.array([0,116+6*math.sin(n*.05),400.])))
 rec=bytearray()
 for bank,mat,pos in poses:rec+=words((mat*16384).flatten().tolist()+pos.tolist())
 rec+=bytes([x[0] for x in poses])+bytes(1)+words([0,512,256,0,768,784+stage*16]);rec+=bytes(208-len(rec))
 notes=[mel[(beat-8)%48] if catplay else 0,0,0,0]
 for m in notes:rec+=bytes(note(m))
 # Real OPLL rhythm mode: snare + tom, matching the two drum heads.
 rhythm=0x2c if bunplay else 0x20
 rec+=bytes([rhythm,0,0,1 if n%8==0 else 0])
 # Poll each instrument in alternate frames; four sprites cover its two mallets.
 side=n%2;arm=poses[4+side];center=[-79,79][side]
 def project(v):return [round(128+230*v[0]/v[2]),round(106-230*v[1]/v[2])]
 for hand in [-21,21]:
  tip=project(arm[1]@np.array([hand,-20,-36])+arm[2])
  surface=project(np.array([center+hand,-50,310]))
  rec+=bytes([tip[1]-4,tip[0]-3,0,0,surface[1]-4 if [catplay,bunplay][side] else 0,surface[0]-3,1,0])
 rec+=bytes([side]);rec+=bytes(256-len(rec));frames+=rec
 if n%8==0:events.append(dict(frame=n,stage=stage,notes=notes,rhythm=rhythm,cat_strike=catplay,bunny_strike=bunplay))
banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384))
while len(banks)<64:banks.append(bytearray(16384))
pal=[]
for rgb in COLORS:
 r,g,b=[round(c/255*7) for c in rgb];pal.extend([(r<<4)|b,g])
(P/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
subprocess.run([str(T/('sdasz80.exe' if (T/'sdasz80.exe').exists() else 'sdasz80')),'-los',str(O/'player.rel'),str(P/'src/player.asm')],cwd=P/'src',check=True)
subprocess.run([str(T/('sdldz80.exe' if (T/'sdldz80.exe').exists() else 'sdldz80')),'-n','-i',str(O/'player'),str(O/'player.rel')],cwd=P,check=True)
for line in (O/'player.ihx').read_text().splitlines():
 r=bytes.fromhex(line[1:]);assert sum(r)%256==0
 if r[3]:continue
 count=r[0];addr=int.from_bytes(r[1:3],'big')
 if addr>=0xD000:assert addr+count<=0xE000;addr=addr-0xD000+0x4100
 banks[0][addr-0x4000:addr-0x4000+count]=r[4:4+count]
rom=b''.join(banks);(O/'PAWS-CONCERT.ROM').write_bytes(rom)
(O/'score.json').write_text(json.dumps(events,indent=2));report=dict(frames=640,bytes=len(rom),sha256=hashlib.sha256(rom).hexdigest(),models=stats);(O/'build.json').write_text(json.dumps(report,indent=2));print(report)
