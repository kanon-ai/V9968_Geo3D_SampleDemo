"""Validate streamed hull geometry, camera records and unchanged combat results."""
from pathlib import Path
import struct,json
import numpy as np
p=Path(__file__).parent
rom=(p/'out/NIGHT_RAVEN_GEO3D.ROM').read_bytes()
assert len(rom)==1048576
counts=[]
for bank in (55,59,60,61,62):
    b=rom[bank*16384:(bank+1)*16384]
    nv,nf,vbytes,fbytes=struct.unpack_from('<BBHH',b)
    counts.append((nv,nf))
    assert nv<=255 and nf<=255 and vbytes==nv*6 and fbytes==nf*11
    for i in range(nf):
        face=b[6+vbytes+i*11:6+vbytes+(i+1)*11]
        assert max(face[:4])<nv
        assert face[10]<16
for f in range(1536):
    values=struct.unpack_from('<15h',rom,56*16384+32*f)
    assert rom[56*16384+32*f+30]==(f*25//320)%5
    m=np.array(values[:9]).reshape(3,3)/16384
    assert np.max(abs(m.T@m-np.eye(3)))<.0002
    assert np.linalg.norm(m@np.array([0,0,320])-values[12:15])<1
    for j in range(5):
        pos=np.array(values[9:12])+j*np.array(values[12:15])
        assert max(abs(pos))<32767
old=json.loads((p/'expected-combat-events.json').read_text())
new=json.loads((p/'out/combat-events.json').read_text())
assert old==new, 'Existing combat event sequence changed'
result=dict(district_vertex_face_counts=counts,hull_instances=5,validated_camera_records=1536,combat_event_sequence_unchanged=True)
(p/'out/hull-validation.json').write_text(json.dumps(result,indent=2))
print(result)
