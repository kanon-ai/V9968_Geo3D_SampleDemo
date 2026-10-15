"""Build separate v2 editions from hash-pinned public ROMs and editable Z80 source.
No graphics, motion or audio assets are regenerated. Requires SDCC_BIN.
"""
from pathlib import Path
import struct,hashlib,json,os,subprocess,re,sys
from collections import Counter
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def assemble(source,out):
 t=Path(os.environ['SDCC_BIN']);exe='.exe' if os.name=='nt' else ''
 subprocess.run([str(t/('sdasz80'+exe)),'-los',str(out/'player.rel'),str(source)],cwd=source.parent,check=True,stdout=subprocess.DEVNULL)
 subprocess.run([str(t/('sdldz80'+exe)),'-n','-i',str(out/'player'),str(out/'player.rel')],cwd=out,check=True,stdout=subprocess.DEVNULL)
 chunks=[]
 for line in (out/'player.ihx').read_text().splitlines():
  r=bytes.fromhex(line[1:]);assert sum(r)%256==0
  if r[3]==0:chunks.append((int.from_bytes(r[1:3],'big'),r[4:4+r[0]]))
 return chunks
def build(spec):
 name=spec['demo'];out=P/'out'/name;out.mkdir(parents=True,exist_ok=True)
 original=(P/'inputs'/spec['name']).read_bytes();assert sha(original)==spec['sha256']
 rom=bytearray(original);src=P/'sources'/name
 asm=(src/'player-v1.asm').read_text()
 lunar=name=='lunar-commute';obs=name=='obsidian'
 count=900 if lunar else 640 if name=='paws-beats' else 512 if obs else 1536
 framebase=11*16384 if obs else 40*16384
 stride=128 if obs else 256
 slotsperframe=9 if obs else 8 if lunar else 7
 ptrbase=202 if lunar else 192 if name=='paws-beats' else 222
 models={};refs=[];sequence=[]
 for f in range(count):
  rec=framebase+f*stride
  for obj in range(slotsperframe):
   if obs:bank=rom[rec+30+obj] if obj<8 else 15;address=0x4000
   else:
    bank=rom[rec+(192 if lunar else 168)+obj]
    address=struct.unpack_from('<H',rom,rec+ptrbase+obj*2)[0] if lunar else 0x4000
   if bank==255:continue
   at=bank*16384+address-0x4000
   nv,nf,vl,fl=struct.unpack_from('<BBHH',rom,at)
   assert 0<nv<=255 and 0<nf<=255 and vl==nv*6 and fl==nf*11,(name,bank,address,nv,nf,vl,fl)
   raw=bytes(rom[at+6:at+6+vl+fl+(0 if obs else nf*8)])
   assert len(raw)==vl+fl+(0 if obs else nf*8)
   key=(nv,nf,raw)
   if key not in models:models[key]=dict(id=len(models)+1,nv=nv,nf=nf,vertices=raw[:vl],faces=raw[vl:vl+fl],uv=raw[vl+fl:])
   mid=models[key]['id'];refs.append((rec,obj,mid,bank,address));sequence.append(mid)
 entries=list(models.values());byid={m['id']:m for m in entries}
 vmax=max(m['nv'] for m in entries);fmax=max(m['nf'] for m in entries)
 nslots=min(8,1023//vmax,1023//fmax);assert nslots>=2
 for m in entries:
  m.update(vstride=vmax,fstride=fmax,layout=0,slot_limit=nslots)
 if name=='four-seasons':
  nslots=5
  for m in entries:
   small=m['nv']<=192 and m['nf']<=192
   m.update(vstride=192 if small else 216,fstride=192 if small else 228,layout=1 if small else 2,slot_limit=5 if small else 4)
 # Greedy placement minimizes bytes transferred over the original draw order.
 # Vertex and topology cache keys are independent; no change in draw order.
 topoids={}
 for m in entries:
  topo=m['faces']+m['uv']
  if topo not in topoids:topoids[topo]=len(topoids)+1
  m['topo']=topoids[topo]
 weights={m['id']:len(m['vertices'])+len(m['faces'])+len(m['uv']) for m in entries}
 freq=Counter(sequence)
 assignment={m['id']:0 for m in entries}
 ranked=sorted(freq,key=lambda k:freq[k]*weights[k],reverse=True)
 # Reserve slots for frequently reused models; stream the long tail through slot 0.
 for slot,mid in enumerate(ranked[:nslots-1],1):assignment[mid]=min(slot,byid[mid]['slot_limit']-1)
 def cost(mapping):
  vertices=[0]*nslots;faces=[0]*nslots;total=0;layout=-1
  for mid in sequence:
   s=mapping[mid];m=byid[mid]
   if layout!=m['layout']:vertices=[0]*nslots;faces=[0]*nslots;layout=m['layout']
   if vertices[s]!=mid:total+=len(m['vertices']);vertices[s]=mid
   if faces[s]!=m['topo']:total+=m['nf']*(12+(0 if obs else 8));faces[s]=m['topo']
  return total
 best=cost(assignment)
 for iteration in range(3):
  changed=False
  for mid in ranked[:48]:
   previous=assignment[mid];chosen=previous
   for s in range(byid[mid]['slot_limit']):
    assignment[mid]=s;c=cost(assignment)
    if c<best:best=c;chosen=s
   assignment[mid]=chosen;changed|=chosen!=previous
  if not changed:break
 if name=='four-seasons':
  # All four seasonal topologies fit together: 654 vertices / 816 faces.
  # Keep those faces/UVs resident across cross-fades, stream only pose vertices.
  nslots=4
  sizes=[(126,180),(192,192),(120,228),(216,216)]
  for m in entries:
   s=sizes.index((m['nv'],m['nf']));assignment[m['id']]=s
   m.update(layout=0,vbase=sum(v for v,f in sizes[:s]),fbase=sum(f for v,f in sizes[:s]))
  best=cost(assignment)
 # Reuse geometry-only banks; keep atlas, motion and music banks separate.
 pool=sorted({b for _,_,_,b,_ in refs});assert 0 not in pool
 if name=='skybound':pool=[b for b in pool if b not in (2,3)] # upper halves contain terrain atlas
 reserved=set(range(framebase//16384,(framebase+count*stride+16383)//16384))
 reserved|=({9,10} if obs else set(range(4,8))|set(range(24,28)) if lunar else set(range(4,11))|set(range(20,36)) if name=='geo3d-basics' else set(range(4,8)) if name in ['skybound','vector-rush'] else set(range(4,15)))
 if name=='skybound':reserved|={2,3}
 assert not set(pool)&reserved,(name,set(pool)&reserved)
 poolindex=0;bank=pool[0];offset=0;packed=bytearray(16384);locations={}
 def flush(b,data):
  while len(rom)<(b+1)*16384:rom.extend(bytes(16384))
  rom[b*16384:(b+1)*16384]=data
 topology_keys={}
 for m in entries:
  s=assignment[m['id']];vf=m.get('vbase',s*m['vstride']);ff=m.get('fbase',s*m['fstride'])
  assert vf+m['nv']<=1023 and ff+m['nf']<=1023
  faces=bytearray()
  for k in range(m['nf']):
   face=m['faces'][k*11:(k+1)*11];ids=[i+vf for i in face[:4]]
   assert all(vf<=i<vf+m['nv'] for i in ids)
   faces+=bytes(i&255 for i in ids)+bytes([sum((i>>8)<<(j*2) for j,i in enumerate(ids))])+face[4:]
   # Decode the new record and prove its original indices/normal/color are unchanged.
   new=faces[-12:];assert [new[j]|(((new[4]>>(j*2))&3)<<8) for j in range(4)]==ids
   assert new[5:]==face[4:]
  tk=(s,m['topo'])
  if tk not in topology_keys:topology_keys[tk]=len(topology_keys)+1
  header=struct.pack('<HHBBBBHHHHH',m['id'],topology_keys[tk],s*4,m['nv'],m['nf'],(8 if name=='geo3d-basics' else 0)|(m['layout']<<4),vf,ff,len(m['vertices']),len(faces),len(m['uv']))
  data=header+m['vertices']+faces+m['uv'];assert len(header)==18 and len(data)<=16384
  if offset+len(data)>16384:
   flush(bank,packed);poolindex+=1
   bank=pool[poolindex] if poolindex<len(pool) else len(rom)//16384
   offset=0;packed=bytearray(16384)
  assert bank<256
  locations[m['id']]=(bank,0x4000+offset);packed[offset:offset+len(data)]=data;offset+=len(data)
 flush(bank,packed)
 if not obs:
  for rec,obj,mid,_,_ in refs:
   b,a=locations[mid];rom[rec+(192 if lunar else 168)+obj]=b;struct.pack_into('<H',rom,rec+ptrbase+obj*2,a)
 else:
  oldbankmap={b:locations[mid] for _,_,mid,b,a in refs}
 # Relocate code only where needed; keep stack, scene record and sound buffers intact.
 if '.org 0xE800' in asm:
  asm=asm.replace('.org 0xE800','.org 0xD000').replace('ld de,#0xE800','ld de,#0xD000').replace('ld bc,#0x0800','ld bc,#0x1000').replace('ld bc,#0x800','ld bc,#0x1000')
 if obs:
  start=asm.index(' ld de,#0x8000\nmodelcache:') if ' ld de,#0x8000\nmodelcache:' in asm else asm.index(' ld de,#0x8000\n ld a,#1\nmodelcache:')
  end=asm.index(' xor a\n out (0x9C),a',start);asm=asm[:start]+asm[end:]
  start=asm.index(' dec a\n add a,a',asm.index('modelnext:'));end=asm.index(' ld a,#0x48',start)
  lookup=''' dec a
 ld l,a
 ld h,#0
 add hl,hl
 ld e,a
 ld d,#0
 add hl,de
 ld de,#v2_world_models
 add hl,de
 ld a,(hl)
 ld (0x6000),a
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 call load_geometry
'''
  asm=asm[:start]+lookup+asm[end:]
  b,a=oldbankmap[15]
  asm=asm.replace(' ld a,#15\n ld (0x6000),a',f' ld a,#{b}\n ld (0x6000),a')
  start=asm.index(' ld a,#0x40',asm.index('; Foreground scout:'));end=asm.index(' ld a,#0x48',start)
  asm=asm[:start]+f' ld hl,#{a}\n call load_geometry\n ld a,#0x5A\n out (0x9D),a\n ld hl,#scoutlight\n ld bc,#0x069F\n otir\n'+asm[end:]
  asm+='\nv2_world_models:\n'+''.join(f' .db {oldbankmap[i][0]}\n .dw {oldbankmap[i][1]}\n' for i in range(1,9))
 else:
  start=asm.index('load_geometry:');end=asm.index('wreg:',start)
  asm=asm[:start]+asm[end:]
  if name=='geo3d-basics':
   waterid=next(mid for _,_,mid,b,_ in refs if b==17)
   asm=asm.replace(' ld a,(MODEL)\n cp #17',f' ld a,(0xE500)\n cp #{waterid}')
  if not lunar:
   pointer=f''' ld a,#7
 ld hl,#COUNT
 sub (hl)
 add a,a
 ld e,a
 ld d,#0
 ld hl,#REC+{ptrbase}
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 call load_geometry'''
   assert asm.count(' call load_geometry')==1
   asm=asm.replace(' call load_geometry',pointer)
 asm=asm.replace('main:\n',' call v2_init\nmain:\n',1)
 if name=='four-seasons':
  start=asm.index('geoblock:');end=asm.index('vramblock:',start)
  fast='geoblock:\n ld c,#0x9F\n ld a,d\n or a\n jr z,v2_fast_tail\nv2_fast_page:\n ld b,#0\nv2_fast_chunk:\n'+' outi\n'*16+' jp nz,v2_fast_chunk\n dec a\n jr nz,v2_fast_page\nv2_fast_tail:\n ld a,e\n or a\n ret z\n ld b,e\n otir\n ret\n'
  asm=asm[:start]+fast+asm[end:]
 asm+='\n'+(P/'cache.asm').read_text()
 for inc in src.glob('*.inc'):(out/inc.name).write_bytes(inc.read_bytes())
 (out/'player.asm').write_text(asm)
 chunks=assemble(out/'player.asm',out)
 rom[:16384]=bytes(16384)
 for address,data in chunks:
  if address>=0xD000:assert address+len(data)<=0xE000,(name,hex(address));address=address-0xD000+0x4100
  assert 0x4000<=address and address+len(data)<=0x8000
  rom[address-0x4000:address-0x4000+len(data)]=data
 size=1<<(len(rom)-1).bit_length();rom.extend(bytes(size-len(rom)))
 allowed=bytearray(len(original));allowed[:16384]=b'\1'*16384
 for b in pool:allowed[b*16384:(b+1)*16384]=b'\1'*16384
 if not obs:
  for rec,obj,mid,_,_ in refs:
   allowed[rec+(192 if lunar else 168)+obj]=1
   allowed[rec+ptrbase+obj*2:rec+ptrbase+obj*2+2]=b'\1\1'
 assert all(ok or before==after for ok,before,after in zip(allowed,original,rom)),'Non-geometry asset or motion changed'
 ranges={}
 for m in entries:
  s=assignment[m['id']]
  ranges[s]=(m.get('vbase',s*m['vstride']),m.get('fbase',s*m['fstride']))
 assert len({v for v,f in ranges.values()})==len(ranges)
 filename=spec['name'].replace('.ROM','-GEO3D-V2.ROM')
 (out/filename).write_bytes(rom)
 report=dict(demo=name,rom=filename,bytes=len(rom),sha256=sha(rom),baseline_sha256=spec['sha256'],frames=count,models=len(entries),slots=nslots,vertex_slot_size=vmax,face_slot_size=fmax,slot_start_addresses=ranges,planned_geometry_bytes=best,assignment=assignment,protected_asset_and_motion_bytes_unchanged=True,extended_face_indices_verified=True)
 (out/'build.json').write_text(json.dumps(report,indent=2));print(name,len(rom),len(entries),nslots,best,flush=True)
if __name__=='__main__':
 for spec in json.loads((P/'manifest.json').read_text()):
  if spec['demo']=='paws-beats':continue
  if len(sys.argv)==1 or spec['demo'] in sys.argv[1:]:build(spec)
