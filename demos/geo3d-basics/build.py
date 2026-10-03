from pathlib import Path
import math,struct,json,subprocess,hashlib,os,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from mesh import Mesh,words
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
def tool(name):
 directory=os.environ.get('SDCC_BIN')
 if directory:
  candidate=Path(directory)/(name+'.exe' if os.name=='nt' else name)
  if candidate.is_file():return str(candidate)
 found=shutil.which(name)
 if not found:raise RuntimeError('Install SDCC and set SDCC_BIN or PATH: '+name)
 return found
def model(plane=False):
 m=Mesh();m.uv=[]
 def face(p,uv):
  for rev in (False,True):
   m.poly(p[::-1] if rev else p,[0,0,0],128)
   m.uv.extend(x for a in (uv[::-1] if rev else uv) for x in a)
 if plane:
  face([(-130,80,0),(130,80,0),(130,-80,0),(-130,-80,0)],[(0,0),(127,0),(127,63),(0,63)])
 else:
  # Three visible faces; geometry and pose remain fixed for the full demo.
  face([(-65,-65,-65),(65,-65,-65),(65,65,-65),(-65,65,-65)],[(0,63),(63,63),(63,0),(0,0)])
  face([(65,-65,-65),(65,-65,65),(65,65,65),(65,65,-65)],[(64,63),(127,63),(127,0),(64,0)])
  face([(-65,65,-65),(65,65,-65),(65,65,65),(-65,65,65)],[(0,0),(63,0),(63,63),(0,63)])
 data=m.data()+bytes(m.uv);return data+bytes(16384-len(data))
def parameters(segment,step):
 angle=2*math.pi*step/32
 f,cx,cy,ty=170,128,110,768
 if segment in (0,3):f=round(170+55*math.sin(angle))
 if segment in (1,3):cx=round(128+40*math.sin(angle));cy=round(110+23*math.sin(angle*2))
 if segment in (2,3):ty=768+step
 return f,cx,cy,ty
def build():
 banks=[bytearray(16384) for _ in range(40)]
 banks[1]=bytearray(model());banks[17]=bytearray(model(True))
 p=[(0,0,0),(41,49,66),(222,239,247),(49,107,148),(82,156,189),(132,197,214),(156,148,206),(90,82,140)]+[(0,0,0)]*248
 p=[tuple(round(c/255*31)*255//31 for c in rgb) for rgb in p]
 palette=bytes(round(c/255*31) for rgb in p for c in rgb)
 (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,palette))+'\n')
 tex=np.zeros((192,256),dtype=np.uint8)
 for y in range(192):
  for x in range(256):
   tex[y,x]=2 if x%16==0 or y%16==0 else (3+((x//16+y//16)%2) if x<64 else (6 if (x//16+y//16)%2 else 7))
 raw=tex.tobytes()
 for i in range(3):banks[8+i]=bytearray(raw[i*16384:(i+1)*16384])
 bg=Image.new('P',(256,256),0);bg.putpalette(sum(map(list,p),[]));d=ImageDraw.Draw(bg)
 d.line((128,18,128,204),fill=1);d.line((8,110,248,110),fill=1)
 d.rectangle((7,20,248,202),outline=1)
 raw=bg.tobytes()
 for i in range(4):banks[4+i]=bytearray(raw[i*16384:(i+1)*16384])
 names=['FOCAL','CENTER','TEX ORIGIN','COMBINED'];font=ImageFont.truetype(os.environ.get('ROM_FONT','C:/Windows/Fonts/consola.ttf' if os.name=='nt' else 'DejaVuSansMono.ttf'),8)
 for label in range(128):
  segment=label//32;step=label%32;f,cx,cy,ty=parameters(segment,step)
  im=Image.new('L',(256,8));draw=ImageDraw.Draw(im)
  draw.text((2,0),f'{names[segment]} F{f:03} X{cx:03} Y{cy:03} T{ty:03}',font=font,fill=255)
  pixels=np.where(np.asarray(im)>80,2,0).astype(np.uint8).tobytes()
  bank=20+label//8;offset=(label%8)*2048;banks[bank][offset:offset+2048]=pixels
 frames=bytearray();audit=[]
 ax=-.28;ay=.50
 rx=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
 ry=np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
 for n in range(1536):
  segment=n//384;step=(n%384)//12;f,cx,cy,ty=parameters(segment,step)
  bank=17 if segment in (2,3) else 1
  mat=np.eye(3) if bank==17 else rx@ry
  poses=[(bank,mat,np.array([0,0,360]))]+[(255,np.eye(3),np.array([0,0,360]))]*6
  rec=bytearray()
  for b,m,pos in poses:rec+=words((m*16384).flatten().tolist()+pos.tolist())
  rec+=bytes(q[0] for q in poses)+bytes(1)+words([0,512,256,0])+words([768,784])
  rec+=words([f,cx,cy,ty])+bytes([segment*32+step]);rec+=bytes(256-len(rec));frames+=rec
  audit.append({'frame':n,'scene':names[segment],'F':f,'CX':cx,'CY':cy,'TEXY':ty})
 banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384))
 subprocess.run([tool('sdasz80'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
 subprocess.run([tool('sdldz80'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
 for line in (OUT/'player.ihx').read_text().splitlines():
  r=bytes.fromhex(line[1:]);assert sum(r)%256==0
  if r[3]==0:
   count=r[0];address=int.from_bytes(r[1:3],'big')
   if address>=0xE800:assert address+count<=0xF000;address=address-0xE800+0x4100
   banks[0][address-0x4000:address-0x4000+count]=r[4:4+count]
 rom=b''.join(banks);assert len(rom)==1048576
 (OUT/'GEO3D-BASICS.ROM').write_bytes(rom)
 (OUT/'parameters.json').write_text(json.dumps(audit,indent=2))
 report={'rom_bytes':len(rom),'sha256':hashlib.sha256(rom).hexdigest(),'scenes':names,'mapper':'ASCII16'}
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
