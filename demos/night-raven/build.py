import os
from pathlib import Path
import math,struct,json,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from mesh import Mesh,words
from hudfont import label
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
TOOL=Path(os.environ['SDCC_BIN']).resolve()
N=1536

def rot(x,y,z):
    cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])

def surface(m,ids,base,center):
    p=np.array([m.v[i] for i in ids[:3]],float);n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
    if np.dot(n,p.mean(axis=0)-center)<0:ids=ids[::-1];n=-n
    if len(ids)==3:ids=ids+[ids[-1]]
    m.f.append((ids,n.tolist(),base))

def aircraft():
    m=Mesh()
    for z,w,h in ((-72,23,12),(-18,28,17),(45,11,9),(118,1,1)):
        m.v += [(-w,0,z),(-w*.65,h,z),(w*.65,h,z),(w,0,z),(w*.6,-h,z),(-w*.6,-h,z)]
    for ring in range(3):
        for k in range(6):surface(m,[ring*6+k,ring*6+(k+1)%6,(ring+1)*6+(k+1)%6,(ring+1)*6+k],1,np.array([0,0,0]))
    for k in range(1,5):surface(m,[0,k,k+1],1,np.array([0,0,0]))
    def prism(points,thick,base):
        first=len(m.v);c=np.array(points).mean(axis=0)
        m.v.extend([(x,y-thick/2,z) for x,y,z in points]+[(x,y+thick/2,z) for x,y,z in points])
        for ids in ([0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]):surface(m,[first+i for i in ids],base,c)
    for s in (-1,1):
        prism([(s*20,0,35),(s*105,5,-34),(s*29,0,-58)],9,1)
        prism([(s*10,3,52),(s*33,1,32),(s*13,3,25)],4,1)
        prism([(s*23,10,-62),(s*42,47,-70),(s*28,12,-22)],5,1)
        m.box(s*26,3,-38,24,24,76,1)
        for k in range(len(m.f)-6,len(m.f)):
            ids,normal,base=m.f[k];m.f[k]=(ids,[v*.55 for v in normal],base)
        # Rear-facing engine emitter.
        x=s*26;m.poly([(x-8,-5,-77),(x+8,-5,-77),(x+8,10,-77),(x-8,10,-77)],[0,0,0],15)
    prism([(-9,18,15),(9,18,15),(0,25,48)],6,10)
    return m

def smoothpath(q, side=1):
    keys=np.array([0,80,150,215,290,370,430,512],float)
    pts=np.array([[320,140,1800],[160,90,1200],[35,-25,700],[300,-120,680],[180,190,1050],[10,80,1300],[-70,210,1550],[320,140,1800]],float)
    pts[:,0]*=side
    q=q%512;i=min(6,int(np.searchsorted(keys,q,side='right')-1))
    tang=[]
    for k in range(8):
        if k in (0,7):v=(pts[1]-pts[6])/(80+512-430)
        else:v=(pts[k+1]-pts[k-1])/(keys[k+1]-keys[k-1])
        tang.append(v)
    dt=keys[i+1]-keys[i];u=(q-keys[i])/dt
    return (2*u**3-3*u*u+1)*pts[i]+(u**3-2*u*u+u)*dt*tang[i]+(-2*u**3+3*u*u)*pts[i+1]+(u**3-u*u)*dt*tang[i+1]

def playerpos(frame):
    return np.array([72*math.sin(frame*.018)+18*math.sin(frame*.043),-65+30*math.sin(frame*.022),330.])

def camera_angles(frame):
    return -.10*math.sin(frame*.022),.16*math.sin(frame*.018)+.06*math.sin(frame*.008),.45*math.sin(frame*.018)

def view(frame):
    return rot(*camera_angles(frame))

def worldpose(frame,j):
    frame=frame%N;q=frame%512;active=1+frame//512
    if j==0:
        v=playerpos(frame+1)-playerpos(frame-1)
        return rot(0,float(v[0])*.075,-float(v[0])*.20)*.85,playerpos(frame)
    if j==active:
        side=1 if (frame//512)%2==0 else -1
        pos=smoothpath(q,side)
        velocity=(smoothpath(q+1,side)-smoothpath(q-1,side))/2
        accel=smoothpath(q+1,side)-2*pos+smoothpath(q-1,side)
        # Camera advances along +Z; orient using world velocity, not relative motion.
        velocity[2]+=2
    else:
        t=math.tau*frame/N+j*1.2566
        pos=np.array([480*math.sin(t),120+100*math.cos(t),1800+250*math.cos(t)])
        velocity=np.array([480*math.cos(t),-100*math.sin(t),-250*math.sin(t)])*math.tau/N
        velocity[2]+=2;accel=np.zeros(3)
    forward=velocity/np.linalg.norm(velocity)
    right=np.cross(np.array([0.,1.,0.]),forward);right/=np.linalg.norm(right)
    up=np.cross(forward,right)
    bank=np.clip(-accel[0]*9,-.85,.85)
    mat=np.column_stack((right,up,forward))@rot(0,0,bank)
    if j<active or (j==active and q>=390):mat*=0 # destroyed; no invisible solid aircraft
    return mat,pos

def pose(frame,j):
    mat,pos=worldpose(frame,j)
    if j==0:return mat,pos
    camera=view(frame)
    return camera@mat,camera@pos

def proj(p):
    if p[2]<=55:return None
    return (128+190*p[0]/p[2],106-190*p[1]/p[2])

def line(a,b,color):
    if a is None or b is None:return struct.pack('<HHHHBBB',0,0,0,0,0,0,0x70)
    a=np.array(a,float);b=np.array(b,float)
    # Liang-Barsky clip, keeping VDP LINE parameters bounded.
    d=b-a;lo=0.;hi=1.
    for p,q in ((-d[0],a[0]),(d[0],255-a[0]),(-d[1],a[1]-15),(d[1],197-a[1])):
        if abs(p)<1e-9:
            if q<0:return line(None,None,0)
        else:
            r=q/p
            if p<0:lo=max(lo,r)
            else:hi=min(hi,r)
    if lo>hi:return line(None,None,0)
    aa=np.rint(a+lo*d).astype(int);bb=np.rint(a+hi*d).astype(int)
    dx,dy=bb-aa;arg=(4 if dx<0 else 0)|(8 if dy<0 else 0)
    dx,dy=abs(int(dx)),abs(int(dy))
    if dy>dx:dx,dy=dy,dx;arg|=1
    return struct.pack('<HHHHBBB',int(aa[0]),int(aa[1]),dx,dy,color,arg,0x70)

COLORS=[(0,0,0),(24,24,24),(48,48,48),(76,76,76),(108,108,108),(152,152,152),(200,200,200),(24,24,24),
        (36,0,18),(72,0,36),(0,56,112),(0,88,152),(0,136,184),(40,188,224),(255,164,32),(255,255,255)]

def build():
    from models import interceptor,drone,heavy,missile,capsule
    from combat import simulate
    meshes=[aircraft(),interceptor(),drone(),heavy(),missile(),capsule()]
    # Reserve palette 14 for guided weapons, including the solid missile body.
    for index,mesh in enumerate(meshes):
        if index==4:
            mesh.f=[(ids,[0,0,0],14) for ids,normal,base in mesh.f]
        elif index==0:
            # One exclusive neutral ink-black material; retain shaded grey undersides
            # and engine/cockpit colours to preserve solid form when banking.
            mesh.f=[(ids,[0,0,0],7) if base==1 and normal[1]>.2
                    else (ids,normal,base) for ids,normal,base in mesh.f]
        else:
            # Keep diffuse ramps below the two reserved weapon/raven slots.
            mesh.f=[(ids,[v*.8 for v in normal] if base==8 else
                         [v*.85 for v in normal] if base==1 else normal,base)
                    for ids,normal,base in mesh.f]
    # All types share a resident vertex pool; only face lists change per RUN.
    vertex_pool=[];lookup={};face_blobs=[]
    for model in meshes:
        remap=[]
        for vertex in model.v:
            key=tuple(vertex)
            if key not in lookup:lookup[key]=len(vertex_pool);vertex_pool.append(vertex)
            remap.append(lookup[key])
        face_blobs.append(b''.join(bytes([remap[i] for i in ids])+words([v*16384 for v in normal])+bytes([base]) for ids,normal,base in model.f))
    assert len(vertex_pool)<=255
    vertices=b''.join(words(v) for v in vertex_pool)
    modelbank=bytearray(16384);modelbank[12]=len(vertex_pool)
    struct.pack_into('<H',modelbank,13,len(vertices));modelbank[16:16+len(vertices)]=vertices
    cursor=16+len(vertices)
    for i,(model,faces) in enumerate(zip(meshes,face_blobs)):
        struct.pack_into('<H',modelbank,i*2,0x4000+cursor)
        data=bytes([len(model.f)])+struct.pack('<H',len(faces))+faces
        modelbank[cursor:cursor+len(data)]=data;cursor+=len(data)
    assert cursor<16384
    banks=[bytearray(16384),modelbank]
    frames,events=simulate(N,worldpose,playerpos,view)
    (OUT/'combat-events.json').write_text(json.dumps(events,indent=2))
    im=Image.new('P',(256,256));im.putpalette(sum([list(c) for c in COLORS],[])+[0]*(768-48));d=ImageDraw.Draw(im)
    # Two reserved dark accent colours form a faint, irregular red nebula.
    yy,xx=np.mgrid[0:256,0:256]
    ridge=76+29*np.sin(xx/63)+12*np.sin(xx/21)
    cloud=np.exp(-((yy-ridge)/31)**2)*(0.58+0.24*np.sin(xx/29+yy/19)+0.18*np.cos(xx/13-yy/23))
    cloud+=0.24*np.exp(-((xx-204)/67)**2-((yy-134)/42)**2)
    cloud*=np.minimum(1,np.minimum(xx,255-xx)/20)*np.minimum(1,np.minimum(yy,255-yy)/20)
    threshold=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])[yy%4,xx%4]/16
    bg=np.zeros((256,256),dtype=np.uint8)
    bg[(cloud>0.12+threshold*.35)&(yy>4)&(yy<252)]=8
    bg[(cloud>0.55+threshold*.5)&(yy>4)&(yy<252)]=9
    im.paste(Image.fromarray(bg))
    d=ImageDraw.Draw(im)
    rng=np.random.default_rng(923)
    for x,y in rng.integers([0,15],[256,197],size=(260,2)):d.point((int(x),int(y)),fill=1)
    font=None
    # Ocean world: spherical light, coherent cloud belts and thin atmosphere.
    # Kept at the existing atlas location/radius so camera motion is unchanged.
    for py in range(48,89):
        for px in range(182,223):
            nx=(px-202)/20;ny=(py-68)/20;r2=nx*nx+ny*ny
            if r2>=1:continue
            nz=math.sqrt(1-r2)
            light=max(0.,-.62*nx-.36*ny+.69*nz)
            longitude=math.atan2(nx,nz);latitude=math.asin(ny)
            # Cloudless planet: subdued ocean, land and spherical shading.
            land=(math.sin(longitude*4.3-latitude*2.8-1.4)
                  +.42*math.cos(longitude*8.1+latitude*6.7))
            if light<.16:shade=1
            elif land>.55:shade=1+min(3,int(light*3.1))
            else:shade=10 if light>.35 else 1
            # Soft neutral limb, not a luminous turquoise outline.
            if nz<.2 and light>.4:shade=3
            d.point((px,py),fill=shade)
    im.save(OUT/'atlas.png');a=np.array(im);bg=bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
    banks.extend([bytearray(bg[:16384]),bytearray(bg[16384:])])
    hud=Image.new('P',(256,256));hud.putpalette(im.getpalette());hd=ImageDraw.Draw(hud)
    for i,score in enumerate((0,1000,3500,8500)):
        y=i*14;label(hd,(5,y),f'NIGHT RAVEN V9968+Geo3D {score:06d}',font=font,fill=15)
        hd.line((5,y+13,250,y+13),fill=10)
    messages=['GUN I / BREAK!', 'GUN I / FIRE', 'TAKE THE POWER-UP', 'SPREAD CANNON UP!',
              'GUN II / ATTACK', 'TAKE MISSILE POD', 'HOMING ONLINE!', 'DODGE / LOCK 2',
              'MISSILES AWAY!', 'HOMING / LOCK', 'KEEP PUSHING!', 'FULL THRUST']
    for i,message in enumerate(messages):
        y=(i+4)*14;hd.line((5,y,250,y),fill=10)
        label(hd,(5,y+2),'SH',font=font,fill=13)
        label(hd,(82,y+2),message,font=font,fill=15 if i not in (3,6,10) else 13)
    hud.save(OUT/'hud-atlas.png');ha=np.array(hud);hudbytes=bytes(((ha[:,::2]<<4)|ha[:,1::2]).flat)
    stars=rng.uniform([-1000,-600,0],[1000,600,1800],(8,3))
    records=bytearray();skyrecords=bytearray()
    for frame,state in enumerate(frames):
        poses=state['objects'];camera=view(frame)
        pitch,yaw,roll=camera_angles(frame)
        scale=.60-.16*frame/N;c=math.cos(roll)*scale;v=math.sin(roll)*scale
        cx=128+30*frame/N-190*scale*math.tan(yaw);cy=128-25*frame/N+190*scale*math.tan(pitch)
        sx=round(cx-128*c+92*v);sy=512+round(cy-128*v-92*c)
        skyrecords+=words([sx,sy,round(c*256),round(v*256)])
        order=sorted(range(6),key=lambda j:poses[j][2][2],reverse=True)
        record=bytearray()
        for j in order:
            kind,mat,pos=poses[j];record+=words((mat*16384).flatten().tolist()+pos.tolist())
        effects=[];shield_overlay=[]
        # Player exhaust anchors velocity and banking to a visible propulsion source.
        _,pm,pp=poses[0]
        for side in (-1,1):
            root=pp+pm@np.array([side*26.,2.,-78.])
            end=pp+pm@np.array([side*26.,2.,-140.-12*math.sin(frame*.65)])
            core=root*.6+end*.4
            effects.append(line(proj(root),proj(end),13))
            effects.append(line(proj(root),proj(core),15))
        # Effects are chosen by gameplay importance, then packed into 32 LINE slots.
        for burst in reversed(state['bursts']):
            age=frame-burst['born'];center=proj(camera@burst['pos'])
            if burst['kind']=='shield':
                if age<20 and not shield_overlay:
                    x,y=proj(playerpos(frame));r=38+age*.85
                    for k in range(6):
                        a=k*math.tau/6;b=(k+1)*math.tau/6
                        shield_overlay.append(line((x+math.cos(a)*r,y+math.sin(a)*r*.65),(x+math.cos(b)*r,y+math.sin(b)*r*.65),15 if age<4 else 13 if age<12 else 11))
                    shield_overlay.append(line((x-r,y-2),(x+2,y-15),13))
                    shield_overlay.append(line((x+2,y-15),(x+r,y-5),13))
                continue
            if center is None:continue
            count=8 if burst['kind']=='kill' else 4
            if burst['kind']=='hit' and age>8:continue
            for k in range(count):
                angle=k*math.tau/count+.06*age;r=2+age*(.9 if burst['kind']=='kill' else .45)
                a=(center[0]+math.cos(angle)*r,center[1]+math.sin(angle)*r)
                b=(center[0]+math.cos(angle)*(r+7),center[1]+math.sin(angle)*(r+7))
                effects.append(line(a,b,15 if age<12 else 13 if age<30 else 3))
            if len(effects)>=8:break
        for missile in state['missiles']:
            trail=missile['trail']
            for age in (0,5,10,18):
                ia=max(0,len(trail)-1-age);ib=max(0,ia-5)
                effects.append(line(proj(camera@trail[ia]),proj(camera@trail[ib]),14))
        pickup=state['pickup']
        if pickup is not None:
            x,y=proj(camera@pickup['pos']);r=12+2*math.sin(frame*.2)
            for a,b in (((x-r,y),(x,y-r)),((x,y-r),(x+r,y)),((x+r,y),(x,y+r)),((x,y+r),(x-r,y))):effects.append(line(a,b,15))
        if state['lock'] or state['warning']:
            x,y=proj(state['target']);r=17 if state['weapon']==3 else 13
            if x<20 or x>235 or y<30 or y>180:
                ax=float(np.clip(x,10,245));ay=float(np.clip(y,23,190))
                direction=np.array([x-128,y-106]);direction/=max(1,np.linalg.norm(direction))
                perpendicular=np.array([-direction[1],direction[0]])
                tip=np.array([ax,ay]);base=tip-direction*10
                effects.extend([line(tip,base+perpendicular*5,15),line(tip,base-perpendicular*5,15)])
            x=float(np.clip(x,20,235));y=float(np.clip(y,30,180))
            col=14 if state['weapon']==3 and state['lock'] else 15 if state['warning'] and frame%12<6 else 13
            for a,b in (((x-r,y-10),(x-r,y+10)),((x+r,y-10),(x+r,y+10)),((x-r,y-10),(x-5,y-10)),((x+5,y+10),(x+r,y+10))):effects.append(line(a,b,col))
            hpmax=state['maxhp']
            effects.append(line((x-r,y-15),(x+r,y-15),3))
            effects.append(line((x-r,y-15),(x-r+2*r*max(0,state['hp'])/hpmax,y-15),13))
        # Threats nearest the player have priority; show both sides' projectiles.
        enemyshots=sorted([s for s in state['shots'] if s['team']],key=lambda s:np.linalg.norm(camera@s['pos']-playerpos(frame)))[:6]
        friendly=[s for s in state['shots'] if not s['team']][-6:]
        for shot in enemyshots+friendly:
            p=shot['pos'];v=p-shot['prev']
            effects.append(line(proj(camera@(p-v*1.7)),proj(camera@p),15 if shot['team'] else 13))
        for s in stars:
            p=s.copy();p[2]=250+(s[2]-frame*52)%1800;p2=p.copy();p2[2]-=45
            effects.append(line(proj(camera@p),proj(camera@p2),4))
        effects=effects[:24]
        effects.extend([line(None,None,0)]*(24-len(effects)))
        effects.extend(shield_overlay+[line(None,None,0)]*(8-len(shield_overlay)))
        record+=b''.join(effects);assert len(record)==496
        scoreindex=(0,1000,3500,8500).index(state['score'])
        sy=768+scoreindex*14;bottom=768+(4+state['message'])*14
        today=[e['event'] for e in events if e['frame'] in (frame,frame+1)]
        sfx=4 if 'shield_guard' in today else 6 if 'enemy_homing_launch' in today else 5 if 'pickup' in today else 4 if 'destroyed' in today else 6 if 'homing_launch' in today else 3 if 'hit' in today else 2 if 'enemy_fire' in today else 1 if 'player_fire' in today else 0
        records+=record+bytes([sfx,state['shield'],0,0,0,0])+struct.pack('<HH',sy,bottom)+bytes([poses[j][0] for j in order])
    banks += [records[i:i+16384] for i in range(0,len(records),16384)]
    assert len(banks)==52
    banks.extend([bytearray(hudbytes[:16384]),bytearray(hudbytes[16384:])])
    assert len(banks)==54
    banks.append(bytearray(skyrecords+bytes(16384-len(skyrecords))))
    from hull import districts
    hulls=districts()
    wd=hulls[0].data();banks.append(bytearray(wd+bytes(16384-len(wd))))
    wr=bytearray()
    for f in range(N):
        cam=view(f)
        escape=max(0.,(f-1150)/386)
        pos=cam@np.array([80*math.sin(f*.008)-1400*escape**2,100*math.sin(f*.011),180-(f*25)%320])
        step=cam@np.array([0,0,320])
        wr+=words((cam*16384).flatten().tolist()+pos.tolist()+step.tolist())+bytes([(f*25//320)%5,0])
    banks.extend(bytearray(wr[i:i+16384]) for i in range(0,len(wr),16384))
    assert len(banks)==59
    for hull in hulls[1:]:
        data=hull.data();banks.append(bytearray(data+bytes(16384-len(data))))
    assert len(banks)==63
    pal=[]
    for r,g,b in COLORS:
        r,g,b=[round(v/255*7) for v in (r,g,b)];pal.extend([(r<<4)|b,g])
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
    subprocess.run([str(TOOL/'sdasz80.exe'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
    subprocess.run([str(TOOL/'sdldz80.exe'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
    for s in (OUT/'player.ihx').read_text().splitlines():
        r=bytes.fromhex(s[1:]);assert sum(r)%256==0
        if r[3]==0:
            n=r[0];a=int.from_bytes(r[1:3],'big')
            if a>=0xE800:assert a+n<=0xF000;a=a-0xE800+0x4100
            assert 0x4000<=a and a+n<=0x8000
            banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
    while len(banks)<64:banks.append(bytearray(16384))
    rom=b''.join(banks);assert len(rom)==1048576
    (OUT/'NIGHT_RAVEN_GEO3D.ROM').write_bytes(rom)
    stats=dict(aircraft_types=['NIGHT RAVEN','interceptor','orbital drone','heavy lancer'],model_vertices=[len(m.v) for m in meshes],model_faces=[len(m.f) for m in meshes],frame_count=N,rom_bytes=len(rom),resident_vertices=len(vertex_pool),geometry_streaming='resident vertex pool; face list on type change, six object slots',combat_events=len(events),sha256=hashlib.sha256(rom).hexdigest())
    (OUT/'manifest.json').write_text(json.dumps(stats,indent=2));print(stats)
if __name__=='__main__':build()
