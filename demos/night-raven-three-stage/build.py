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
    phase=math.tau*frame/N
    return -.07*math.sin(phase*3),.12*math.sin(phase*2)+.04*math.sin(phase),.26*math.sin(phase*2)

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
    meshes=[aircraft(),interceptor(),drone(),heavy(),missile(),capsule(),aircraft()]
    meshes[5].v=[tuple(c*2 for c in v) for v in meshes[5].v]
    # Reserve palette 14 for guided weapons, including the solid missile body.
    for index,mesh in enumerate(meshes):
        if index==4:
            mesh.f=[(ids,[0,0,0],14) for ids,normal,base in mesh.f]
        elif index==6:
            mesh.f=[(ids,[n*.28 for n in normal],5 if base==1 else base) for ids,normal,base in mesh.f]
        elif index==5:
            mesh.f=[(ids,[n*.35 for n in normal],11) for ids,normal,base in mesh.f]
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
    modelbank=bytearray(16384);modelbank[14]=len(vertex_pool)
    struct.pack_into('<H',modelbank,15,len(vertices));modelbank[32:32+len(vertices)]=vertices
    cursor=32+len(vertices)
    for i,(model,faces) in enumerate(zip(meshes,face_blobs)):
        struct.pack_into('<H',modelbank,i*2,0x4000+cursor)
        data=bytes([len(model.f)])+struct.pack('<H',len(faces))+faces
        modelbank[cursor:cursor+len(data)]=data;cursor+=len(data)
    assert cursor<16384
    banks=[bytearray(16384),modelbank]
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
    # Game HUD replaces the precomputed combat captions.
    hud=Image.new('P',(256,256));hud.putpalette(im.getpalette());hd=ImageDraw.Draw(hud)
    label(hd,(4,2),'NIGHT RAVEN / SECTOR',fill=15)
    label(hd,(185,2),'SCORE',fill=13)
    hd.line((4,13,251,13),fill=10)
    label(hd,(2,17),'SH',fill=13);label(hd,(94,17),'MS',fill=14)
    label(hd,(148,17),'X MISSILE',fill=15)
    for k in range(10):label(hd,(k*8,32),str(k),fill=15)
    panels=[['NIGHT RAVEN / DEV DEMO','ARROWS OR JOYSTICK','SPACE FIRE  X MISSILE','HOLD AIM TO LOCK','SPACE TO LAUNCH'],
            ['RAVEN LOST','BREAK THE INTERCEPTION','SPACE TO RETRY','F1 RESTART  ESC PAUSE'],
            ['DEFENCE CORE DESTROYED','FLIGHT TEST COMPLETE','SPACE TO FLY AGAIN','NIGHT RAVEN'],
            ['PAUSED','ESC TO RESUME','F1 RESTART']]
    for i,lines in enumerate(panels):
        for j,t in enumerate(lines):label(hd,((256-len(t)*6)//2,44+i*54+j*9),t,fill=14 if j==0 else 15)
    hud.save(OUT/'hud-atlas.png');ha=np.array(hud);hudbytes=bytes(((ha[:,::2]<<4)|ha[:,1::2]).flat)
    stars=rng.uniform([-1000,-600,0],[1000,600,1800],(8,3))
    records=bytearray();skyrecords=bytearray()
    for frame in range(N):
        pitch,yaw,roll=camera_angles(frame)
        phase=math.tau*frame/N
        scale=.54+.06*math.cos(phase);c=math.cos(roll)*scale;v=math.sin(roll)*scale
        cx=128+15*math.sin(phase)-190*scale*math.tan(yaw);cy=128-12*math.sin(phase)+190*scale*math.tan(pitch)
        sx=round(cx-128*c+92*v);sy=512+round(cy-128*v-92*c)
        skyrecords+=words([sx,sy,round(c*256),round(v*256)])
    records=bytearray(N*512)
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
        phase=math.tau*f/N
        pos=cam@np.array([55*math.sin(phase*2),55*math.sin(phase*3),180-(f*25)%320])
        step=cam@np.array([0,0,320])
        quantized=words((cam*16384).flatten().tolist()+pos.tolist()+step.tolist())
        from visibility import visible_mask
        first=(f*25//320)%5
        mask=31
        wr+=quantized+bytes([first,mask])
    banks.extend(bytearray(wr[i:i+16384]) for i in range(0,len(wr),16384))
    assert len(banks)==59
    for hull in hulls[1:]:
        data=hull.data();banks.append(bytearray(data+bytes(16384-len(data))))
    assert len(banks)==63
    # Solid corridor and a much larger reactor chamber share 320-unit modules.
    for bank,width,height in [(4,360,240),(5,1300,850),(36,360,240)]:
        room=Mesh()
        room.box(-width,0,160,60,height*2,320,1)
        room.box(width,0,160,60,height*2,320,1)
        room.box(0,-height,160,width*2,50,320,1)
        room.box(0,height,160,width*2,50,320,1)
        for side in (-1,1):
            room.box(side*(width-36),0,16,16,height*2,16,10)
            room.box(0,side*(height-28),16,width*2,12,16,10)
        if bank==4:
            # Raised armour overlaps the wall surface; gaps remain recessed.
            # Alternate lengths and heights avoid a uniform ladder silhouette.
            for side in (-1,1):
                room.box(side*323,-96,108,42,116,152,3)
                room.box(side*314,82,222,60,92,146,1)
                room.box(side*298,-96,103,18,72,104,1)
                room.box(side*289,82,231,14,48,82,3)
                room.box(side*321,12,67,44,24,92,3)
                room.box(side*314,158,143,56,22,210,1)
            # Ceiling and floor service housings retain a clear central passage.
            room.box(-172,-210,156,154,38,198,3)
            room.box(143,-190,202,112,72,90,1)
            room.box(175,211,110,144,36,146,3)
            room.box(-153,203,251,118,52,82,1)
        if bank==5:
            room.box(-760,0,130,75,1500,70,3)
            room.box(760,0,130,75,1500,70,3)
            room.box(0,-430,200,2200,28,110,3)
            # Distant three-dimensional octagonal gantry makes the chamber scale visible.
            for k in range(8):
                angle=math.tau*k/8
                beam=Mesh();beam.box(0,0,0,520,40,70,3)
                m=rot(0,0,angle+math.pi/2)
                off=len(room.v)
                room.v.extend([tuple(m@np.array(v)+np.array([650*math.cos(angle),650*math.sin(angle),1100])) for v in beam.v])
                room.f.extend([([i+off for i in ids],(m@np.array(n)).tolist(),base) for ids,n,base in beam.f])
            room.box(0,-390,900,1400,18,32,11)
        room.f=[(ids,[0,0,0],11) if base==10 else (ids,n,base) for ids,n,base in room.f]

        if bank in (4,36):
            # Interior-only camera: discard outward faces hidden by the wall.
            # Keep inward and depth faces so the raised armour retains parallax.
            room.f=[(ids,n,base) for ids,n,base in room.f
                    if not any(n[axis]*sum(room.v[i][axis] for i in ids)>0
                               for axis in (0,1))]
        # Camera stays inside the module and looks along +Z. Far-facing
        # end faces cannot contribute visible pixels; omit them before transfer.
        room.f=[(ids,n,base) for ids,n,base in room.f if n[2]<=0]
        if bank==4:
            # Split long inner wall faces without changing their surfaces.
            # Geo3D drops a whole face when a vertex crosses the near plane.
            def clip_z(poly,z,keep_above):
                out=[]
                for a,b in zip(poly,poly[1:]+poly[:1]):
                    ia=(a[2]>=z) if keep_above else (a[2]<=z)
                    ib=(b[2]>=z) if keep_above else (b[2]<=z)
                    if ia:out.append(a)
                    if ia!=ib:
                        t=(z-a[2])/(b[2]-a[2])
                        out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
                return out
            fs=[]
            for ids,n,base in room.f:
                poly=[room.v[i] for i in ids]
                if max(ids)<32 and max(v[2] for v in poly)-min(v[2] for v in poly)>128:
                    for z in reversed(range(0,320,128)):
                        pp=clip_z(clip_z(poly,z,True),z+128,False)
                        if len(pp)==4:
                            off=len(room.v);room.v.extend(pp)
                            fs.append((list(range(off,off+4)),n,base))
                else:fs.append((ids,n,base))
            room.f=fs
        used=sorted({i for ids,n,base in room.f for i in ids})
        remap={v:i for i,v in enumerate(used)}
        room.v=[room.v[i] for i in used]
        room.f=[([remap[i] for i in ids],n,base) for ids,n,base in room.f]
        if bank==5:chamber_model=room
        data=room.data();banks[bank]=bytearray(data+bytes(16384-len(data)))
    # Prototype: open service lane between staggered machinery, no enclosing rings.
    for bank in (4,36):
        room=Mesh()
        cuts=[0,106,213,320] if bank==4 else [0,320]
        for z0,z1 in zip(cuts,cuts[1:]):
            room.poly([(-1100,640,z0),(1100,640,z0),(1100,640,z1),(-1100,640,z1)],[0,0,0],2)
        for side in (-1,1):
            z=70 if side<0 else 242
            # Broad industrial units, separated in depth and across the route.
            room.box(side*580,-20,z,340,390,108,2)
            room.box(side*590,192,z,390,34,134,3)
            room.box(side*592,-225,z,320,24,96,3)
            if bank in (4,36):
                room.box(side*474,-30,z,90,190,64,3)
                room.box(side*780,-290,z,90,350,52,2)
                # Pipe in the gap; not a wall covering the whole view.
                room.box(side*430,280,z,28,122,28,3)
            x=side*407
            for y0,y1,col in ((-142,-126,12),(-106,-100,10),(108,116,14)):
                pts=[(x,y0,z-38),(x,y1,z-38),(x,y1,z+38),(x,y0,z+38)]
                room.poly(pts[::-1 if side>0 else 1],[0,0,0],col)
        room.f=[(ids,n,base) for ids,n,base in room.f if n[2]<=0]
        assert len(room.v)<=248,(bank,len(room.v))
        data=room.data();banks[bank]=bytearray(data+bytes(16384-len(data)))
    # Quiet central flight lane with asymmetric recessed service bays at its edges.
    floor=Mesh()
    def deck_face(points,col,toward):
        aa,bb,cc=np.array(points[:3],float)
        if np.dot(np.cross(bb-aa,cc-aa),toward)<0:points=points[::-1]
        floor.poly(points,[0,0,0],col)
    def deck_top(x0,x1,z0,z1,y=-237,col=3):
        for zz in range(z0,z1,96):
            end=min(z1,zz+96)
            deck_face([(x0,y,zz),(x1,y,zz),(x1,y,end),(x0,y,end)],col,(0,1,0))
    deck_top(-180,180,0,320)
    for side in (-1,1):
        start,end=(38,138) if side<0 else (178,278)
        # Side strips remain level with the original column plinths.
        for lo,hi in ((180,238),(388,1100)):
            xx=sorted((side*lo,side*hi));deck_top(*xx,0,320)
        xx=sorted((side*238,side*388));x0,x1=xx
        deck_top(x0,x1,0,start);deck_top(x0,x1,end,320)
        deck_top(x0,x1,start,end,-279,1)
        # Four real cavity walls; no black texture pasted onto a flat floor.
        for x,toward in ((x0,(1,0,0)),(x1,(-1,0,0))):
            deck_face([(x,-279,start),(x,-237,start),(x,-237,end),(x,-279,end)],4 if side*x<0 else 2,toward)
        deck_face([(x0,-279,start),(x1,-279,start),(x1,-237,start),(x0,-237,start)],2,(0,0,1))
        deck_face([(x0,-279,end),(x1,-279,end),(x1,-237,end),(x0,-237,end)],4,(0,0,-1))
        # A low bevelled access cover offset from the pit and from the opposite side.
        z=226 if side<0 else 74
        xa,xb=sorted((side*190,side*330))
        deck_top(xa+12,xb-12,z-24,z+24,-221,4)
        deck_face([(xa,-237,z-36),(xb,-237,z-36),(xb-12,-221,z-24),(xa+12,-221,z-24)],3,(0,1,-1))
        deck_face([(xa+12,-221,z+24),(xb-12,-221,z+24),(xb,-237,z+36),(xa,-237,z+36)],2,(0,1,1))
        for x,inner,normal in ((xa,xa+12,(-1,1,0)),(xb,xb-12,(1,1,0))):
            deck_face([(x,-237,z-36),(inner,-221,z-24),(inner,-221,z+24),(x,-237,z+36)],3,normal)
        # Tiny inset equipment indicator, away from the flight silhouette.
        deck_top(side*300-4,side*300+4,start+24,start+46,-277,12)
    unique=[];lookup={};remap={}
    for i,v in enumerate(floor.v):
        key=tuple(round(c) for c in v)
        if key not in lookup:lookup[key]=len(unique);unique.append(key)
        remap[i]=lookup[key]
    floor.v=unique
    floor.f=[([remap[i] for i in ids],n,col) for ids,n,col in floor.f]
    assert len(floor.v)<=248,len(floor.v)
    data=floor.data();banks[38]=bytearray(data+bytes(16384-len(data)))
    blank=Mesh();blank.v=[(0,0,100)]
    data=blank.data();banks[39]=bytearray(data+bytes(16384-len(data)))
    # Rival poses: true rotated polygons, varying depth and crossing passes.
    rival=bytearray()
    # Approach, close crossing attack, banking retreat and re-entry.
    # Smooth periodic keyframes preserve position/velocity across the loop.
    keys=np.array([[128,44,50],[89,55,115],[53,78,184],
                   [194,53,190],[204,31,117],[151,26,47],
                   [83,41,66],[171,63,136]],float)
    def rival_path(q):
        q=(q%256)/32; k=int(q);t=q-k
        a,b,c,d=[keys[j%8] for j in (k-1,k,k+1,k+2)]
        v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
        v=np.clip(v,[38,20,32],[218,88,205])
        return v
    def rival_world(q):
        x,y,age=rival_path(q);z=(256-age)*8
        return np.array([(x-128)*z/170,(106-y)*z/170,z])
    for i in range(256):
        x,y,age=rival_path(i)
        velocity=rival_world(i+1)-rival_world(i-1)
        forward=velocity/np.linalg.norm(velocity)
        right=np.cross(np.array([0.,1.,0.]),forward);right/=np.linalg.norm(right)
        up=np.cross(forward,right)
        bank=.65*math.sin(math.tau*i/128)
        matrix=np.column_stack((right,up,forward))@rot(0,0,bank)*.95
        rival+=words((matrix*16384).flatten())
        rival+=bytes([round(x),round(y),round(age),0])+bytes(10)
    banks[17]=bytearray(rival+bytes(16384-len(rival)))
    cards=Image.new('P',(256,128));cards.putpalette(im.getpalette());cd=ImageDraw.Draw(cards)
    for i,(title,subtitle) in enumerate([('01 / OUTER BREACH','BREAK THE INTERCEPTION'),('02 / REACTOR VAULT','ENTER THE FORTRESS'),('03 / WHITE RAVEN','ONE AGAINST ONE')]):
        label(cd,((256-len(title)*6)//2,i*40+8),title,fill=14)
        label(cd,((256-len(subtitle)*6)//2,i*40+23),subtitle,fill=15)
    ca=np.array(cards);cb=bytes(((ca[:,::2]<<4)|ca[:,1::2]).flat)
    banks[18]=bytearray(cb)
    # Dedicated title artwork in unused ROM banks and VRAM rows 1280-1535.
    title=Image.new('P',(256,256));title.putpalette(im.getpalette());td=ImageDraw.Draw(title)
    trng=np.random.default_rng(73)
    for x,y in trng.integers([0,0],[256,212],size=(120,2)):
        td.point((int(x),int(y)),fill=3 if x%3 else 5)
    for k in range(6):
        td.polygon([(0,72+k*5),(256,20+k*8),(256,36+k*8),(0,91+k*5)],fill=1 if k%2 else 0)
    td.ellipse((174,67,248,141),fill=3);td.ellipse((181,65,254,135),fill=1)
    # Original black-raven silhouette, swept wings and twin engine nacelles.
    td.polygon([(126,80),(144,120),(223,157),(154,149),(142,164),(111,164),(100,149),(30,157),(109,120)],fill=7)
    td.polygon([(126,80),(132,130),(144,151),(126,143),(109,153),(121,125)],fill=4)
    td.polygon([(113,127),(108,149),(101,156),(107,127)],fill=2)
    td.polygon([(140,127),(146,149),(153,156),(147,127)],fill=2)
    td.line((112,152,110,158),fill=13,width=2);td.line((142,152,144,158),fill=13,width=2)
    # Original geometric wordmark, drawn as a 16-color title asset.
    glyphs={
        'R':[[(0,8),(0,0),(4,0),(5,1),(5,3),(4,4),(0,4)],[(3,4),(5,8)]],
        'A':[[(0,8),(0,2),(2,0),(3,0),(5,2),(5,8)],[(0,5),(5,5)]],
        'V':[[(0,0),(0,4),(2.5,8),(5,4),(5,0)]],
        'E':[[(5,0),(0,0),(0,8),(5,8)],[(0,4),(4,4)]],
        'N':[[(0,8),(0,0),(5,8),(5,0)]]}
    mask=Image.new('L',(224,39));md=ImageDraw.Draw(mask)
    for i,ch in enumerate('RAVEN'):
        for path in glyphs[ch]:
            pts=[(round(5+i*42+x*6+(8-y)*1.0),round(3+y*4)) for x,y in path]
            md.line(pts,fill=255,width=6,joint='curve')
    # A restrained steel face and cyan lower edge; black cut separates halves.
    arr=np.array(mask)>0
    for dy,dx,color in [(3,2,10),(1,0,13)]:
        for y,x in zip(*np.where(arr)):title.putpixel((12+int(x)+dx,41+int(y)+dy),color)
    for y,x in zip(*np.where(arr)):
        title.putpixel((12+int(x),41+int(y)),15 if y<17 else (6 if y<24 else 5))
    td.line((17,61,232,61),fill=0)
    small=Image.new('P',(30,9));small.putpalette(im.getpalette())
    label(ImageDraw.Draw(small),(0,0),'NIGHT',fill=15)
    title.paste(small.resize((90,18),Image.Resampling.NEAREST),(25,17))
    td.line((128,25,226,25),fill=10)
    td.line((188,27,225,27),fill=13)
    for y,text,color in [(84,'THE BLACK WING STRIKES BACK',13),(174,'SPACE / FIRE TO LAUNCH',14),(189,'ARROWS MOVE   X MISSILE',6),(203,'TURBOR + V9968 + GEO3D',13)]:
        label(td,((256-len(text)*6)//2,y),text,fill=color)
    title.save(OUT/'title-screen.png')
    ta=np.array(title);tb=bytes(((ta[:,::2]<<4)|ta[:,1::2]).flat)
    banks[19]=bytearray(tb[:16384]);banks[20]=bytearray(tb[16384:])
    bursts=bytearray()
    for life in range(1,33):
        age=32-life;seg=[]
        if age<8:
            radius=8+age*.6
            for j in range(16):
                y=j-8
                half=round(math.sqrt(max(0,radius*radius-y*y)))
                offset=round(2*math.sin(j*2.1+age))
                seg += [offset-half,y,offset+half,y]
        else:
            t=age-8
            for j in range(16):
                a=j*2.399963;speed=.75+(j%5)*.22
                r=8+t*speed
                trail=max(1,6-t*.18)
                x=math.cos(a);y=math.sin(a)*.75
                seg += [round(x*(r-trail)),round(y*(r-trail)),round(x*r),round(y*r)]
        bursts.extend(v&255 for v in seg)
    banks[21]=bursts+bytearray(16384-len(bursts))



    # Bank 63: smooth pitch/bank poses and forward optical-flow segments.
    visual=bytearray(16384)
    for pitch in range(9):
        for bank in range(17):
            pose=rot((pitch-4)*.035,(bank-8)*.01875,-(bank-8)*.04375)*.65
            at=(pitch*17+bank)*18
            visual[at:at+18]=words((pose*16384).flatten())
    for f in range(64):
        for j in range(8):
            angle=j*math.tau/8+.22
            depth=24+(120-(f*5+j*19)%120)
            far=2100/depth;near=2100/max(16,depth-10)
            xy=[]
            for radius in (far,near):
                xy += [round(np.clip(128+math.cos(angle)*radius*1.5,2,253)),round(np.clip(101+math.sin(angle)*radius*.85,16,193))]
            at=4096+f*32+j*4
            visual[at:at+4]=bytes(xy)
    banks.append(visual)
    # SCREEN 8 / EPAL: visible pages 0/256, sky 512, compact HUD 768.
    sky8=np.array(im,dtype=np.uint8)
    h8=Image.new('P',(256,256));dd=ImageDraw.Draw(h8)
    label(dd,(4,2),'NIGHT RAVEN / SECTOR',fill=15);label(dd,(185,2),'SCORE',fill=13)
    dd.line((4,13,251,13),fill=10)
    label(dd,(2,17),'SH',fill=13);label(dd,(94,17),'MS',fill=14);label(dd,(148,17),'X MISSILE',fill=15)
    for k in range(10):label(dd,(k*8,32),str(k),fill=15)
    for y,lines in [(44,['RAVEN LOST','SPACE TO RETRY','F1 RESTART  ESC PAUSE']),
                    (84,['MISSION COMPLETE','WHITE RAVEN DEFEATED','SPACE TO FLY AGAIN']),
                    (124,['PAUSED','ESC TO RESUME','F1 RESTART'])]:
        for j,t in enumerate(lines):label(dd,((256-len(t)*6)//2,y+j*9),t,fill=14 if j==0 else 15)
    for i,t in enumerate(['01 / OUTER BREACH','02 / REACTOR VAULT','03 / WHITE RAVEN']):
        label(dd,((256-len(t)*6)//2,154+i*30+4),t,fill=14)
        label(dd,(77,154+i*30+16),'NEXT SECTOR',fill=15)
    def packed(a):
        return ((a[:,::2]<<4)|a[:,1::2]).tobytes()
    resources=packed(sky8)+packed(np.array(h8,dtype=np.uint8))
    for k in range(4):banks[22+k]=bytearray(resources[k*16384:(k+1)*16384])
    rawtitle=packed(np.array(title,dtype=np.uint8))
    for k in range(2):banks[30+k]=bytearray(rawtitle[k*16384:(k+1)*16384])
    # Original 16-bar minor-key theme: repeatable two-bar motif, then response.
    # None releases a note; -1 holds it without another attack.
    fnums=[172,182,193,205,217,230,244,258,274,290,307,326]
    motif=[(0,None),(24,64),(26,67),(28,64),(30,None)]
    score=bytearray()
    roots=[40,40,40,40,36,36,38,38,40,40,40,40,36,36,38,38]
    for step in range(256):
        bar,t=divmod(step,16);root=roots[bar]
        bass=(root+12 if t==14 else root) if t%2==0 else None
        lead=dict(motif).get(step%64,-1)
        # Second half answers the same motif, avoiding a stream of unrelated notes.
        if lead not in (None,-1) and bar in (6,7,14,15):lead-=2
        pad=root+12 if t==0 else (None if t==15 else -1)
        fifth=root+19 if t==0 else (None if t==15 else -1)
        for note in (bass,lead,pad,fifth):
            if note==-1:score.extend((0,255))
            elif note is None:score.extend((0,0))
            else:
                fn=fnums[note%12];block=note//12-1
                score.extend((fn&255,16|(block<<1)|(fn>>8)))
    banks[34]=score+bytearray(16384-len(score))
    pal=[]
    for r,g,b in COLORS:
        r,g,b=[round(v/255*7) for v in (r,g,b)]
        pal.extend([(r<<4)|b,g])
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
    subprocess.run([str(TOOL/'sdasz80.exe'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
    subprocess.run([str(TOOL/'sdldz80.exe'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
    for s in (OUT/'player.ihx').read_text().splitlines():
        r=bytes.fromhex(s[1:]);assert sum(r)%256==0
        if r[3]==0:
            n=r[0];a=int.from_bytes(r[1:3],'big')
            if a>=0xC300:assert a+n<=0xE200;a=a-0xC300+0x4100
            assert 0x4000<=a and a+n<=0x8000
            banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
    while len(banks)<64:banks.append(bytearray(16384))
    rom=b''.join(banks);assert len(rom)==1048576
    (OUT/'NIGHT_RAVEN_THREE_STAGE.ROM').write_bytes(rom)
    stats=dict(aircraft_types=['NIGHT RAVEN','interceptor','orbital drone','heavy lancer'],model_vertices=[len(m.v) for m in meshes],model_faces=[len(m.f) for m in meshes],frame_count=N,rom_bytes=len(rom),resident_vertices=len(vertex_pool),geometry_streaming='resident vertex pool; face list on type change, six object slots',gameplay='runtime input, combat, collision, locks, missiles, shield, progression, boss and retry',demo_combat_records_used=False,sha256=hashlib.sha256(rom).hexdigest())
    (OUT/'manifest.json').write_text(json.dumps(stats,indent=2));print(stats)
if __name__=='__main__':build()
