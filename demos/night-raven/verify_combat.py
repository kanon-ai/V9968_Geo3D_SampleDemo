"""Checks causality, guidance, HUD/mesh records and scene safety."""
import json,struct,hashlib
from pathlib import Path
import numpy as np
from build import N,worldpose,playerpos,view
from combat import simulate
ROOT=Path(__file__).resolve().parent
frames,events=simulate(N,worldpose,playerpos,view)
assert events==json.loads((ROOT/'out/combat-events.json').read_text())
deaths=[e for e in events if e['event']=='destroyed']
assert len(deaths)==3 and len({e['enemy'] for e in deaths})==3
passed=[e for e in events if e['event']=='passed']
spawns=[e for e in events if e['event']=='spawn']
assert len(passed)>=25 and len(passed)>len(deaths)*5
assert len(spawns)==len(passed)+len(deaths)+3
assert all(len(set(st['enemy_ids']))==3 for st in frames)
assert any(e['event']=='enemy_homing_launch' for e in events)
assert any(e['event']=='shield_guard' for e in events)
pickups=[e for e in events if e['event']=='pickup']
assert [e['weapon'] for e in pickups]==[2,3]
assert deaths[0]['frame']<pickups[0]['frame']<512
assert deaths[1]['frame']<pickups[1]['frame']<1024
launch=next(e for e in events if e['event']=='homing_launch')
impact=next(e for e in events if e['event']=='missile_impact')
assert pickups[1]['frame']<launch['frame']<impact['frame']
assert frames[-1]['score']==8500 and min(f['shield'] for f in frames)>0
max_turn=0.;minimum_distance=1e9;max_visible=0
for f,state in enumerate(frames):
    assert all(0<=s<=8 for s in [state['shield']])
    max_visible=max(max_visible,sum(o[0]!=255 for o in state['objects']))
    for kind,mat,pos in state['objects']:
        assert np.isfinite(mat).all() and np.isfinite(pos).all()
        assert np.max(np.abs(mat))<1.1
        if 1<=kind<=3:
            minimum_distance=min(minimum_distance,float(np.linalg.norm(pos-playerpos(f))))
            assert pos[2]>100
    for missile in state['missiles']:
        trail=missile['trail']
        if len(trail)>2:
            a,b=trail[-1]-trail[-2],trail[-2]-trail[-3]
            angle=np.arccos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))
            max_turn=max(max_turn,float(angle))
assert max_turn<=.13
assert minimum_distance>180 # separation exceeds the simulated collision cores
rom=(ROOT/'out/NIGHT_RAVEN_GEO3D.ROM').read_bytes()
assert len(rom)==1048576
bank=rom[16384:32768];vertices=bank[12];assert vertices<=255
faces=[]
for model in range(6):
    address=struct.unpack_from('<H',bank,model*2)[0]-0x4000
    count=bank[address];size=struct.unpack_from('<H',bank,address+1)[0]
    assert size==count*11 and count<=255
    blob=bank[address+3:address+3+size]
    assert all(max(blob[i:i+4])<vertices for i in range(0,size,11))
    faces.append(count)
for f,state in enumerate(frames):
    record=rom[4*16384+f*512:4*16384+(f+1)*512]
    assert len(record)==512
    sy,by=struct.unpack_from('<HH',record,502)
    assert 768<=sy<=810 and sy%14==768%14
    assert 824<=by<=978
    assert record[497]==state['shield']
    assert all(k in range(6) or k==255 for k in record[506:512])
    for i in range(32):
        x,y,major,minor,color,arg,cmd=struct.unpack_from('<HHHHBBB',record,144+i*11)
        assert 0<=x<=255 and 0<=y<=197 and minor<=major<=255 and cmd==0x70
sky_records=rom[54*16384:54*16384+N*8]
assert len(set(sky_records[i:i+8] for i in range(0,len(sky_records),8)))>300
assert any(e['event']=='enemy_fire' and e['enemy']>1+e['frame']//512 for e in events)
report=dict(frames=N,events=len(events),destroyed=[d['frame'] for d in deaths],pickups=[p['frame'] for p in pickups],
    missile_launch=launch['frame'],missile_impact=impact['frame'],max_missile_turn_degrees=float(np.degrees(max_turn)),
    spawned=len(spawns),passed=len(passed),shield_guards=sum(e['event']=='shield_guard' for e in events),minimum_enemy_player_distance=minimum_distance,final_score=frames[-1]['score'],final_shield=frames[-1]['shield'],
    resident_vertices=vertices,max_visible_objects=max_visible,face_counts=faces,
    rom_sha256=hashlib.sha256(rom).hexdigest(),scope='Offline combat simulation and packed ROM validation; hardware performance unverified')
(ROOT/'out/combat-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
