"""Deterministic automatic pilot and combat simulation, baked into ROM records.

Health, projectile hits, pickups and homing guidance are simulated here.
The MSX plays the resulting state stream and Geo3D renders its solid geometry.
"""
import math
import numpy as np

def unit(v):
    return v/max(1e-9,np.linalg.norm(v))

def facing(v,bank=0):
    f=unit(v);r=unit(np.cross([0.,1.,0.],f));u=np.cross(f,r)
    c,s=math.cos(bank),math.sin(bank)
    return np.column_stack((r*c+u*s,u*c-r*s,f))

def simulate(n,worldpose,playerpos,view):
    enemies=[None]*3;serial=0;shots=[];missiles=[];hostiles=[];bursts=[];pickup=None
    score=0;kills=0;weapon=1;shield=8;last_damage=-100;last_launch=-100
    frames=[];events=[];dead={};speed=18.
    def spawn(slot,f,initial=False):
        nonlocal serial
        serial+=1;kind=(1,2,1,3)[(serial-1)%4];side=1 if serial%2 else -1
        e=dict(uid=serial,kind=kind,born=f,z0=(1000+slot*750 if initial else 2450+100*(serial%3)),speed=speed+kind*2,
               side=side,hp=(3,5,12)[kind-1],maxhp=(3,5,12)[kind-1])
        enemies[slot]=e;events.append(dict(frame=f,event='spawn',slot=slot,enemy=serial,kind=kind))
    def location(e,f):
        age=f-e['born'];z=e['z0']-e['speed']*age
        t=np.clip((e['z0']-z)/max(1,e['z0']-200),0,1)
        # Inbound interception all the way past the player's plane; never retreat in Z.
        x=e['side']*(40+235*t*t)+28*math.sin(age*.035+e['uid'])
        y=(90 if e['uid']%3 else -160)+25*math.sin(age*.026+e['uid'])
        return np.array([x,y,z],float)
    for slot in range(3):spawn(slot,0,True)
    for f in range(n):
        camera=view(f);pp=playerpos(f);pw=camera.T@pp
        for slot,e in enumerate(enemies):
            if e is None:spawn(slot,f);continue
            if location(e,f)[2]<-160:
                events.append(dict(frame=f,event='passed',slot=slot,enemy=e['uid']))
                spawn(slot,f)
        if pickup is not None:
            age=f-pickup['born'];u=min(1.,age/65)
            pickup['pos']=pickup['origin']*(1-u)+(pw+np.array([0.,8.,30.]))*u
            if np.linalg.norm(pickup['pos']-pw)<48:
                weapon=min(3,weapon+1);events.append(dict(frame=f,event='pickup',weapon=weapon))
                bursts.append(dict(pos=pw.copy(),born=f,kind='pickup'));pickup=None
        if shield<8 and f%48==0:shield+=1
        candidates=[e for e in enemies if e is not None and 600<location(e,f)[2]<1650]
        target=min(candidates,key=lambda e:location(e,f)[2]) if candidates else max(enemies,key=lambda e:location(e,f)[2])
        targetpos=location(target,f)
        # Every inbound enemy fires. No wave completion gate controls spawning.
        for e in enemies:
            p=location(e,f);age=f-e['born']
            if 550<p[2]<1650 and age%24==7:
                count=2 if e['kind']==1 else 3 if e['kind']==2 else 5
                for offset in np.linspace(-50,50,count):
                    aim=view(f+35).T@np.array([float(offset),-45.,330.])
                    shots.append(dict(pos=p.copy(),prev=p.copy(),vel=(aim-p)/35,team=1,age=0,damage=1))
                events.append(dict(frame=f,event='enemy_fire',enemy=e['uid'],kind=e['kind'],count=count))
        # Invaders use homing weapons to stop a fast intruder; shields intercept them.
        for e in enemies:
            p=location(e,f);age=f-e['born']
            if e['kind']>=2 and age%45==20 and 850<p[2]<2100 and len(hostiles)<2:
                side=e['side'];origin=p+np.array([side*45.,0.,0.])
                hostiles.append(dict(pos=origin.copy(),vel=np.array([side*17.,8.,-15.]),trail=[origin.copy()],age=0,enemy=True))
                events.append(dict(frame=f,event='enemy_homing_launch',enemy=e['uid']))
        incoming=[]
        for m in hostiles:
            current=unit(m['vel']);desired=unit(pw-m['pos'])
            angle=math.acos(float(np.clip(np.dot(current,desired),-1,1)))
            blend=min(1.,.12/max(angle,1e-6))
            m['vel']=unit(current*(1-blend)+desired*blend)*min(46,np.linalg.norm(m['vel'])+1.1)
            m['pos']+=m['vel'];m['age']+=1;m['trail'].append(m['pos'].copy());m['trail']=m['trail'][-32:]
            if np.linalg.norm(m['pos']-pw)<115:
                shield=max(0,shield-1);last_damage=f
                bursts.append(dict(pos=pw.copy(),born=f,kind='shield'))
                events.append(dict(frame=f,event='shield_guard',shield=shield))
            elif m['age']<110:incoming.append(m)
        hostiles=incoming
        # Fire only to make a gap. The rest of the defenders are overtaken alive.
        fight=(kills==0 and 100<f<420) or (kills==1 and 560<f<920)
        if fight and candidates and f%14==0:
            events.append(dict(frame=f,event='player_fire',weapon=weapon))
            for offset in ((-12,12) if weapon==1 else (-30,0,30)):
                origin=camera.T@(pp+np.array([offset*.7,0.,68.]))
                travel=max(1,round(np.linalg.norm(targetpos-origin)/(60+target['speed'])))
                aim=location(target,f+travel)+np.array([offset*.6,0,0])
                shots.append(dict(pos=origin.copy(),prev=origin.copy(),vel=unit(aim-origin)*60,team=0,age=0,damage=1))
        if weapon==3 and kills==2 and 1050<f<1450 and candidates and not missiles and f-last_launch>50:
            last_launch=f
            for side in (-1,1):
                origin=camera.T@(pp+np.array([side*48.,0.,0.]))
                missiles.append(dict(pos=origin.copy(),vel=camera.T@np.array([side*20.,8.,18.]),trail=[origin.copy()],age=0,target=target['uid']))
            events.append(dict(frame=f,event='homing_launch',count=2,target=target['uid']))
        def damage(e,amount,p):
            nonlocal kills,score,pickup
            if e not in enemies:return
            e['hp']-=amount;events.append(dict(frame=f,event='hit',enemy=e['uid'],damage=amount,hp=max(0,e['hp'])))
            bursts.append(dict(pos=p.copy(),born=f,kind='hit'))
            if e['hp']<=0:
                kills+=1;score=(0,1000,3500,8500)[min(kills,3)];dead[e['uid']]=f
                events.append(dict(frame=f,event='destroyed',enemy=e['uid'],score=score))
                bursts.append(dict(pos=p.copy(),born=f,kind='kill'))
                if kills<3:pickup=dict(origin=p.copy(),pos=p.copy(),born=f)
                slot=enemies.index(e);spawn(slot,f)
        alive=[]
        for s in shots:
            s['prev']=s['pos'].copy();s['pos']+=s['vel'];s['age']+=1;used=False
            if s['team']==0:
                for e in list(enemies):
                    p=location(e,f);v=s['pos']-s['prev'];u=np.clip(np.dot(p-s['prev'],v)/max(1,np.dot(v,v)),0,1)
                    if np.linalg.norm(s['prev']+v*u-p)<(55,65,100)[e['kind']-1]:
                        damage(e,s['damage'],p);used=True;break
            elif np.linalg.norm(s['pos']-pw)<25 and f-last_damage>=60:
                shield=max(0,shield-1);last_damage=f;used=True
                events.append(dict(frame=f,event='shield_guard',shield=shield))
                bursts.append(dict(pos=pw.copy(),born=f,kind='shield'))
            if not used and s['age']<70 and s['pos'][2]>-200:alive.append(s)
        shots=alive;flying=[]
        for m in missiles:
            e=next((e for e in enemies if e['uid']==m['target']),None)
            if e is None:continue
            p=location(e,f);desired=unit(location(e,f+2)-m['pos']);current=unit(m['vel'])
            angle=math.acos(float(np.clip(np.dot(current,desired),-1,1)))
            blend=min(1.,.12/max(angle,1e-6));m['vel']=unit(current*(1-blend)+desired*blend)*min(52,np.linalg.norm(m['vel'])+1.5)
            m['pos']+=m['vel'];m['age']+=1;m['trail'].append(m['pos'].copy());m['trail']=m['trail'][-28:]
            if np.linalg.norm(m['pos']-p)<100:
                damage(e,8,p);events.append(dict(frame=f,event='missile_impact',enemy=e['uid']))
            elif m['age']<90:flying.append(m)
        missiles=flying
        pm,_=worldpose(f,0);objects=[(0,pm,pp)]
        for e in enemies:
            p=location(e,f);v=location(e,f+1)-p+np.array([0,0,10.]);mat=facing(v,-.4*math.sin((f-e['born'])*.03))
            cp=camera@p
            objects.append((e['kind'] if cp[2]>130 else 255,camera@mat,cp))
        visible_missiles=(missiles+hostiles)[:2]
        for slot in range(2):
            if slot<len(visible_missiles):
                m=visible_missiles[slot];objects.append((4,camera@facing(m['vel']),camera@m['pos']))
            elif slot==0 and pickup is not None:
                a=f*.07;c,s=math.cos(a),math.sin(a)
                objects.append((5,camera@np.array([[c,0,s],[0,1,0],[-s,0,c]]),camera@pickup['pos']))
            else:objects.append((255,np.zeros((3,3)),np.array([0.,0.,1000.])))
        bursts=[b for b in bursts if f-b['born']<34]
        recent=next((e for e in reversed(events) if e['event']=='pickup'),None)
        warning=any(300<location(e,f)[2]<1400 for e in enemies)
        lock=fight or (weapon==3 and kills==2 and f>1020)
        if f>1460:message=10
        elif recent and f-recent['frame']<45:message=3 if weapon==2 else 6
        elif missiles:message=8
        elif pickup is not None:message=2 if weapon==1 else 5
        elif lock:message=1 if weapon==1 else 4 if weapon==2 else 9
        elif warning:message=0 if weapon==1 else 4 if weapon==2 else 7
        else:message=11
        frames.append(dict(objects=objects,shots=[dict(pos=s['pos'].copy(),prev=s['prev'].copy(),team=s['team']) for s in shots],
            missiles=[dict(pos=m['pos'].copy(),trail=[p.copy() for p in m['trail']],enemy=m.get('enemy',False)) for m in visible_missiles],bursts=[dict(b) for b in bursts],
            pickup=None if pickup is None else dict(pickup),weapon=weapon,shield=shield,score=score,active=target['kind'],
            target=camera@targetpos,hp=max(0,target['hp']),maxhp=target['maxhp'],warning=warning,lock=lock,message=message,dead=dict(dead),
            enemy_ids=[e['uid'] for e in enemies]))
    return frames,events
