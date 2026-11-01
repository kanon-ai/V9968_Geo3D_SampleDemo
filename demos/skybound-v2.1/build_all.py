from pathlib import Path
import os,sys,subprocess,shutil,json,hashlib
P=Path(__file__).resolve().parent;W=P/'_work';W.mkdir(exist_ok=True)
assert os.environ.get('SDCC_BIN'),'Set SDCC_BIN to the SDCC assembler/linker bin directory.'
def run(file):subprocess.run([sys.executable,str(file)],cwd=P,check=True)
run(P/'build.py')
v=W/'v2';v.mkdir(exist_ok=True)
shutil.copy2(P/'tools/v2_build.py',v/'build_v2.py');shutil.copy2(P/'tools/cache.asm',v/'cache.asm')
(v/'inputs').mkdir(exist_ok=True);(v/'sources/skybound').mkdir(parents=True,exist_ok=True)
r=P/'out/SKYBOUND-JAPAN.ROM';shutil.copy2(r,v/'inputs'/r.name)
shutil.copy2(P/'src/player.asm',v/'sources/skybound/player-v1.asm')
for f in (P/'src').glob('*.inc'):shutil.copy2(f,v/'sources/skybound'/f.name)
(v/'manifest.json').write_text(json.dumps([dict(demo='skybound',name=r.name,sha256=hashlib.sha256(r.read_bytes()).hexdigest())]))
run(v/'build_v2.py')
d=W/'dual';d.mkdir(exist_ok=True);name='skybound-japan-v2'
shutil.copy2(P/'tools/dual_build.py',d/'build_dual.py')
for x in [d/'sources'/name,d/'inputs'/name]:x.mkdir(parents=True,exist_ok=True)
r=v/'out/skybound/SKYBOUND-JAPAN-GEO3D-V2.ROM'
for f in [r.parent/'player.asm',*r.parent.glob('*.inc')]:shutil.copy2(f,d/'sources'/name/f.name)
shutil.copy2(r,d/'inputs'/name/r.name)
(d/'manifest.json').write_text(json.dumps([dict(id=name,asset=r.name,sha256=hashlib.sha256(r.read_bytes()).hexdigest())]))
run(d/'build_dual.py')
output=P/'out/rom';output.mkdir(exist_ok=True)
for f in (d/'out'/name).glob('*.ROM'):shutil.copy2(f,output/f.name)
print('Rebuilt both I/O editions in',output)
