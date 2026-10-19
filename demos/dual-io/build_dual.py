from pathlib import Path
import re,json,os,subprocess,hashlib,shutil,sys
P=Path(__file__).resolve().parent
T=Path(os.environ['SDCC_BIN'])
EXE='.exe' if os.name=='nt' else ''
def sha(b):return hashlib.sha256(b).hexdigest()
def assemble(src,out):
 out.mkdir(parents=True,exist_ok=True)
 subprocess.run([str(T/('sdasz80'+EXE)),'-los',str(out/'player.rel'),str(src)],cwd=src.parent,check=True,stdout=subprocess.DEVNULL)
 subprocess.run([str(T/('sdldz80'+EXE)),'-n','-i',str(out/'player'),str(out/'player.rel')],cwd=out,check=True,stdout=subprocess.DEVNULL)
 code={}
 for line in (out/'player.ihx').read_text().splitlines():
  r=bytes.fromhex(line[1:]);assert sum(r)%256==0
  if r[3]==0:
   a=int.from_bytes(r[1:3],'big');code.update({a+i:b for i,b in enumerate(r[4:4+r[0]])})
 return code

def convert(text):
 changes=[];lines=[]
 for n,line in enumerate(text.splitlines(),1):
  cmd=line.split(';')[0];new=cmd
  if re.match(r'\s*(out\s*\(|in\s+a,\s*\()',cmd,re.I):
   new=re.sub(r'0x(9[89ABCDF])\b',lambda m:'0x'+format(int(m[1],16)-16,'02X'),cmd,flags=re.I)
  elif re.match(r'\s*ld\s+(bc|c),\s*#0x',cmd,re.I):
   m=re.search(r'#0x([0-9a-f]+)',cmd,re.I);v=int(m[1],16)
   if (v&255) in [0x98,0x99,0x9a,0x9b,0x9c,0x9d,0x9f]:new=cmd[:m.start(1)]+format(v-16,'0'+str(len(m[1]))+'X')+cmd[m.end(1):]
  if cmd!=new:changes.append(dict(line=n,before=cmd.strip(),after=new.strip()))
  lines.append(new+line[len(cmd):])
 return '\n'.join(lines)+'\n',changes

def build(s):
 name=s['id'];src=P/'sources'/name;out=P/'out'/name;out.mkdir(parents=True,exist_ok=True)
 rom=(P/'inputs'/name/s['asset']).read_bytes();assert sha(rom)==s['sha256']
 asm=(src/'player.asm').read_text(encoding='utf-8-sig');internal=assemble(src/'player.asm',out/'internal')
 # Recover each RAM relocation from the explicit boot copy instructions.
 reloc=[]
 for m in re.finditer(r'ld hl,#(0x[0-9A-Fa-f]+)\s+ld de,#(0x[0-9A-Fa-f]+)\s+ld bc,#(0x[0-9A-Fa-f]+)',asm):
  a,b,n=map(lambda x:int(x,16),m.groups())
  if 0x4000<=a<0x8000 and b>=0xc000:reloc.append((b,b+n,a))
 assert reloc,(name,'no relocation')
 def offset(a):
  if 0x4000<=a<0x8000:return a-0x4000
  for lo,hi,base in reloc:
   if lo<=a<hi:return a-lo+base-0x4000
  raise ValueError((name,'unmapped',hex(a)))
 mismatches=[(hex(a),b,rom[offset(a)]) for a,b in internal.items() if b!=rom[offset(a)]]
 if mismatches:
  print(name,'BASELINE MISMATCH',len(mismatches),mismatches[:5],flush=True);return False
 exttext,changes=convert(asm);extsrc=out/'external-src';extsrc.mkdir(exist_ok=True)
 for f in src.glob('*.inc'):
  txt,cs=convert(f.read_text());(extsrc/f.name).write_text(txt)
  for c in cs:c['file']=f.name
  changes+=cs
 (extsrc/'player.asm').write_text(exttext)
 external=assemble(extsrc/'player.asm',out/'external');assert internal.keys()==external.keys()
 diff=[a for a in internal if internal[a]!=external[a]]
 assert len(diff)==len(changes) and len(diff)>10,(name,len(diff),len(changes))
 data=bytearray(rom)
 for a in diff:
  assert internal[a]-external[a]==16,(name,a)
  data[offset(a)]=external[a]
 assert sum(a!=b for a,b in zip(rom,data))==len(diff)
 # Separate filenames are unique even when upstream basenames are reused.
 stem=name.upper();(out/(stem+'-INTERNAL-98H.ROM')).write_bytes(rom);(out/(stem+'-EXTERNAL-88H.ROM')).write_bytes(data)
 report=dict(id=name,relocations=reloc,code_bytes=len(internal),operand_changes=changes,rom_offsets=[offset(a) for a in diff],internal_sha256=sha(rom),external_sha256=sha(data),bytes=len(rom))
 (out/'build.json').write_text(json.dumps(report,indent=2));print(name,'OK',len(diff),'port operands',flush=True);return True
if __name__=='__main__':
 specs=json.loads((P/'manifest.json').read_text());ok=[]
 for s in specs:
  if len(sys.argv)>1 and s['id'] not in sys.argv[1:]:continue
  ok.append(build(s))
 assert all(ok),'Baseline source mismatch: no changed ROM was produced for those variants'
