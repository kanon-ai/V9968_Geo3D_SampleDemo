
from pathlib import Path
import struct,json,hashlib
P=Path(__file__).resolve().parent
old=(P.parent/'night-raven-opll-test/out/NIGHT_RAVEN_GEO3D.ROM').read_bytes()
new=(P/'out/NIGHT_RAVEN_GEO3D.ROM').read_bytes()
assert len(new)==len(old)==1048576
assert new[32768:]==old[32768:], 'Scene records, art or music changed'
bank=new[16384:32768];vs=bank[256:256+4944];fs=bank[256+4944:256+4944+6324]
for group in range(11):
 vf,ff,nv,nf=struct.unpack_from('<4H',bank,group*8)
 assert vf+nv<=824 and ff+nf<=527
 if group<6:
  ob=old[16384:32768];start=struct.unpack_from('<H',ob,group*2)[0]-0x4000
  count=ob[start];size=struct.unpack_from('<H',ob,start+1)[0];source=ob[start+3:start+3+size]
  assert vs[vf*6:(vf+nv)*6]==ob[16:16+nv*6]
 else:
  idx=[55,59,60,61,62][group-6];ob=old[idx*16384:(idx+1)*16384]
  count=ob[1];size=struct.unpack_from('<H',ob,4)[0];vb=struct.unpack_from('<H',ob,2)[0]
  source=ob[6+vb:6+vb+size]
  assert vs[vf*6:(vf+nv)*6]==ob[6:6+vb]
 assert count==nf
 for j in range(nf):
  f=fs[(ff+j)*12:(ff+j+1)*12];o=source[j*11:(j+1)*11]
  indices=[f[k]+(((f[4]>>(2*k))&3)<<8) for k in range(4)]
  assert indices==[x+vf for x in o[:4]]
  assert f[5:]==o[4:]
results=json.loads((P/'comparison/results.json').read_text())
assert results['v2-emu-v2-rom']['matching_vram_pages']==512
assert results['v2-emu-v2-rom']['music_matching_prefix']
assert results['v2-emu-v2-rom']['rom_sha256']==hashlib.sha256(new).hexdigest()
print('PASS: all 11 models, 824 vertices, 527 faces, unchanged scene/art/music banks, 512 identical rendered pages')
