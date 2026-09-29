"""Verify the published ROM builds, mesh references and captured media limits."""
from pathlib import Path
import hashlib,json,struct,math
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES={'vector-rush':'VECTOR_RUSH','skybound':'SKYBOUND','orbital':'ORBITAL'}
for name,romname in NAMES.items():
    data=(ROOT/'demos'/name/'out'/f'{romname}.ROM').read_bytes()
    expected=json.loads((ROOT/'docs/validation'/f'{name}-original-build.json').read_text())
    assert len(data)==1048576,(name,'ROM size')
    assert hashlib.sha256(data).hexdigest()==expected['sha256'],(name,'release hash mismatch')
    models=[1,2,3] if name=='orbital' else [1,2,3,*range(8,40)]
    for bank in models:
        d=data[bank*16384:(bank+1)*16384]
        nv,nf,vb,fb=struct.unpack_from('<BBHH',d)
        assert 0<nv<=255 and 0<nf<=255 and vb==nv*6 and fb==nf*11
        assert 6+vb+fb+(0 if name=='vector-rush' else nf*8)<=16384
        for f in range(nf):
            assert max(d[6+vb+11*f:10+vb+11*f])<nv
            if d[6+vb+11*f+10]&128:
                uv=d[6+vb+fb+8*f:6+vb+fb+8*(f+1)]
                assert len(uv)==8
                if name=='orbital' and bank in (1,2):
                    assert all((0 if bank==1 else 64)<=v<=(63 if bank==1 else 127) for v in uv[1::2])
    for frame in range(1536):
        d=data[40*16384+frame*256:40*16384+(frame+1)*256]
        assert all(b==255 or b in models for b in d[168:175])
        assert struct.unpack_from('<H',d,184)[0]==768
        assert 784<=struct.unpack_from('<H',d,186)[0]<=1008
        if name=='orbital':
            ids=list(d[168:175]);ei=ids.index(1);mi=ids.index(2)
            earth=struct.unpack_from('<3h',d,ei*24+18);moon=struct.unpack_from('<3h',d,mi*24+18)
            matrix=struct.unpack_from('<9h',d,mi*24)
            facing=[matrix[i] for i in (2,5,8)];direction=[e-m for e,m in zip(earth,moon)]
            dot=sum(x*y for x,y in zip(facing,direction))/(math.sqrt(sum(x*x for x in facing))*math.sqrt(sum(x*x for x in direction)))
            assert dot>math.cos(math.radians(.2)), 'Moon facing error'

    gif=ROOT/'docs/media'/f'{name}.gif'
    assert gif.stat().st_size<15000000
    with Image.open(gif) as im:
        for i in range(im.n_frames):
            im.seek(i);im.load()
    print(name, 'PASS: ROM hash, mesh/UV references, frame banks, HUD ranges, GIF decode/size')
