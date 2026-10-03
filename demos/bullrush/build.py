from pathlib import Path
import math,struct,json,subprocess,hashlib,os,shutil
import numpy as np
from PIL import Image,ImageDraw
from mesh import Mesh,words
from hudfont import label
from motion import trajectory
from robot import body_pose,compressed_vertices
import city
import textures
import pursuit
import color256
import occlusion
ROOT=Path(__file__).parent.resolve();OUT=ROOT/'out';OUT.mkdir(exist_ok=True)
def tool(name):
    directory=os.environ.get('SDCC_BIN')
    if directory:
        candidate=Path(directory)/(name+'.exe' if os.name=='nt' else name)
        if candidate.is_file():return str(candidate)
    found=shutil.which(name)
    if not found:raise RuntimeError('Install SDCC and add its bin directory to PATH or set SDCC_BIN: '+name)
    return found
N=576;LENGTH=960;F=170
COLORS=[(0,0,0),(24,28,32),(48,56,64),(80,88,96),(144,152,152),(232,224,200),(132,100,64),(224,132,32),(255,208,64),(80,104,88),(40,64,56),(48,80,104),(88,128,152),(168,192,200),(112,136,144),(160,136,112)]
def unit(v):return v/max(np.linalg.norm(v),1e-9)
def road(s):return np.array([900*math.sin(s/1900)+480*math.sin(s/850),0,s])
def axes(s):
    forward=unit(road(s+1)-road(s-1));right=unit(np.cross([0,1,0],forward))
    return np.column_stack((right,np.array([0,1,0]),forward))
def ry(a):return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def rx(a):return np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
def rz(a):return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def point(s,x,y=0):return road(s)+axes(s)@np.array([x,y,0])
def face(m,pts,col,normal=(0,0,0)):
    p=np.array(pts,float);n=np.cross(p[1]-p[0],p[2]-p[0])
    # Road polygons have an upward-facing winding.
    if n[1]<0:p=p[::-1]
    m.poly(p.tolist(),normal,col)
def clean(m):
    vertices=[];mapping={};remap=[]
    for v in m.v:
        key=tuple(round(x) for x in v)
        if key not in mapping:mapping[key]=len(vertices);vertices.append(key)
        remap.append(mapping[key])
    m.v=vertices;m.f=[([remap[i] for i in ids],normal,base) for ids,normal,base in m.f]
    return m
def flat(m):
    m.f=[(ids,[0,0,0],max(1,min(15,c+(1 if n[1]>0 else -1 if n[0]<0 else 0)))) for ids,n,c in m.f]
    return clean(m)
def car(part,lean=0,crouch=0):
    m=Mesh()
    if part==1:
        # Original tapered armor: narrow waist, longer exposed legs, enclosed skates.
        def armor(x,y,z,w,h,d,c,top=1,bottom=1,sweep=0):
            first=len(m.v);m.box(x,y,z,w,h,d,c)
            for j in range(first,len(m.v)):
                vx,vy,vz=m.v[j];upper=vy>y;scale=top if upper else bottom
                m.v[j]=(x+(vx-x)*scale,vy,vz+(sweep if upper else 0))
        armor(0,111,1,64,29,38,5,1.08,.40,11)
        armor(0,88,0,18,18,18,2,.7,1)
        armor(0,77,0,36,12,23,4,.75,1)
        armor(0,134,0,16,10,16,2)
        armor(0,146,3,22,14,26,4,.55,1,7)
        armor(0,147,16,19,4,3,8,.75,1)
        # Compact split cooling pack, no wing or shoulder booster silhouette.
        for side in (-1,1):
            armor(side*15,109,-20,15,30,17,4,.4,1,-9)
            armor(side*15,109,-27,6,18,2,1)
            armor(side*37,122,0,27,19,31,5,1.28,.4,10)
            armor(side*42,104,0,11,20,13,2)
            armor(side*44,87,2,16,28,25,4,.55,1,7)
            armor(side*44,70,5,12,12,15,2)
            armor(side*17,59,0,15,31,19,4,.75,1,-4)
            armor(side*18,43,8,18,10,13,2)
            armor(side*20,33,3,20,24,28,5,.45,1,10)
            armor(side*24,24,4,27,13,46,4,.70,1,-4)
            armor(side*37,122,-15,13,10,3,7,.70,1)
        for side in (-1,1):armor(side*25,109,-21,10,32,15,5,.4,1,-7)
        armor(0,113,-29,5,24,3,8)
    else:
        # Axle along X: rotating segmented tire, side hubs and amber tread.
        n=12
        for i in range(n):
            a=i*2*math.pi/n;b=(i+1)*2*math.pi/n
            pts=[(x,29*math.cos(t),29*math.sin(t)) for x,t in [(-14,a),(14,a),(14,b),(-14,b)]]
            m.poly(pts,[0,0,0],2 if i%3 else 7)
            for x in (-14,14):
                pts=[(x,0,0),(x,29*math.cos(a),29*math.sin(a)),(x,29*math.cos(b),29*math.sin(b))]
                m.poly(pts if x>0 else pts[::-1],[0,0,0],3 if i%2 else 4)
        m.box(0,0,0,32,12,12,7)
        for side in (-1,1):
            m.box(side*17,0,0,3,17,17,4)
            for a in (0,math.pi/2,math.pi,math.pi*1.5):
                m.box(side*17,20*math.cos(a),20*math.sin(a),3,4,4,8)
    if part==1:
        # Rigid transforms per armor part: boots stay planted while the joints flex.
        for start in range(0,len(m.v),8):
            pts=np.array(m.v[start:start+8]);center=pts.mean(axis=0)
            if abs(center[0])>35 and center[1]>65:
                pivot=np.array([math.copysign(42,center[0]),122,0])
                pts=(rx(-.28-.35*crouch+math.copysign(1,center[0])*lean*.18)@(pts-pivot).T).T+pivot
                if center[1]<100:
                    pivot=np.array([math.copysign(48,center[0]),103,-8])
                    pts=(rx(.35*crouch)@(pts-pivot).T).T+pivot
            if center[1]>80:
                pivot=np.array([0,80,0]);pts=(rz(-lean*.12)@rx(.14+.20*crouch)@(pts-pivot).T).T+pivot
                pts[:,1]-=6*crouch
            elif abs(center[0])<28 and center[1]>47:
                pivot=np.array([center[0],75,0])
                pts=(rx(-.32*crouch)@(pts-pivot).T).T+pivot
                pts[:,1]-=4*crouch
            elif abs(center[0])<22 and center[1]>28:
                pivot=np.array([center[0],20,0])
                pts=(rx(.28*crouch)@(pts-pivot).T).T+pivot
            if center[1]>138:
                pivot=np.array([0,135,3]);pts=(ry(lean*.32)@(pts-pivot).T).T+pivot
            elif abs(center[0])>35 and center[1]>65:
                pivot=np.array([math.copysign(37,center[0]),122,0])
                pts=(rz(-lean*.16)@(pts-pivot).T).T+pivot
            elif abs(center[0])<28 and 28<center[1]<80:
                pts[:,1]-=math.copysign(1,center[0])*lean*2
            m.v[start:start+8]=pts.tolist()
    m.v=[(x*.73,y-8,z*.85) for x,y,z in m.v] if part==1 else [(x*.64,y*.48,z*.48) for x,y,z in m.v]
    return flat(m)
def chunk(index):
    m=Mesh();origin=np.array([(index%8)*960.,0.,(index//8)*960.])
    # A city tile: intersecting north/south and east/west streets.
    face(m,[[-480,0,-480],[480,0,-480],[480,0,480],[-480,0,480]],2)
    for x in (-330,330):
        for z in (-330,330):
            face(m,[[x-145,2,z-145],[x+145,2,z-145],[x+145,2,z+145],[x-145,2,z+145]],4)
            h=340+((index*7+int(x+z))%5)*110
            m.box(x,h/2+3,z,280,h,280,4 if index%2 else 14)
            m.box(x,h+26,z,215,46,215,3)
            m.box(x,h+63,z,120,30,140,4)
            m.box(x,h*.18,z,300,22,300,3)
            # Window bands on both street-facing walls, all real geometry.
            for flip in (-1,1):
                y=h*.24
                xx=x+flip*141;zz=z+flip*141
                pts=[[xx,y,z-115],[xx,y+h*.50,z-115],[xx,y+h*.50,z+115],[xx,y,z+115]]
                m.poly(pts,[0,0,0],11);m.poly(pts[::-1],[0,0,0],11)
                pts=[[x-115,y,zz],[x+115,y,zz],[x+115,y+h*.50,zz],[x-115,y+h*.50,zz]]
                m.poly(pts,[0,0,0],11);m.poly(pts[::-1],[0,0,0],11)
    for a in (-410,-270,270,410):
        face(m,[[-3,1,a-35],[3,1,a-35],[3,1,a+35],[-3,1,a+35]],8)
        face(m,[[a-35,1,-3],[a+35,1,-3],[a+35,1,3],[a-35,1,3]],8)
    return flat(m),origin

def packmesh(m,kind=None,robot=False,blue=False):
    uv=bytes(len(m.f)*8)
    if robot or kind is not None:m,uv=textures.mapped(m,kind,blue)
    d=m.data()+uv;assert len(d)<=16384
    return bytearray(d+bytes(16384-len(d)))
def bitmap(im):
    a=np.array(im);return bytes(((a[:,::2]<<4)|a[:,1::2]).flat)
def build():
    banks=[bytearray(16384),packmesh(body_pose()[0],robot=True),packmesh(car(2)),packmesh(car(3))]
    sky=Image.new('P',(256,256),12);sky.putpalette(sum([list(c) for c in COLORS],[])+[0]*720);d=ImageDraw.Draw(sky)
    d.rectangle((0,0,255,58),fill=11);d.rectangle((0,59,255,104),fill=12);d.rectangle((0,105,255,150),fill=13)
    d.rectangle((0,151,255,255),fill=13)
    sky.save(OUT/'sky.png');b=bitmap(sky);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    hud=Image.new('P',(256,256));hud.putpalette(sky.getpalette());d=ImageDraw.Draw(hud)
    label(d,(4,0),'BULLRUSH / T:TEXTURE',fill=5)
    for i in range(15):
        y=16+i*16
        label(d,(5,y),['ROLLER DASH','SLIDE LEFT','SLIDE RIGHT','PIVOT TURN','DASH TURN'][i%5]+' / AUTO DEMO',fill=5)
        d.line((4,y+13,251,y+13),fill=11)
    d.rectangle((0,240,255,255),fill=0)
    label(d,(4,240),'SEARCH / CITY PATROL',fill=5)
    hud.save(OUT/'hud.png');b=bitmap(hud);banks.extend([bytearray(b[:16384]),bytearray(b[16384:])])
    tile_models=[city.tile_mesh(kind) for kind in city.KINDS]
    banks.extend(packmesh(m,kind=kind) for m,kind in zip(tile_models,city.KINDS))
    banks.extend(bytearray(16384) for _ in range(16-len(banks)))
    chunks=[(tile_models[city.KINDS.index(city.tile_kind(i))],city.origin(i)) for i in range(32)]
    assert len(banks)==16
    bounds={8+i:np.array([[x,y,z] for x in (-480,480) for y in (0,city.MAP['districts'][kind]['height']+80) for z in (-480,480)]) for i,kind in enumerate(city.KINDS)}
    for bank in (1,55):bounds[bank]=np.array([[x,y,z] for x in (-100,100) for y in (0,180) for z in (-100,100)])
    for bank in (2,3):bounds[bank]=np.array([[x,y,z] for x in (-24,24) for y in (-36,36) for z in (-36,36)])
    def outside(bank,matrix,position):
        pts=(matrix@bounds[bank].T).T+position;x,y,z=pts.T
        return bool(np.all(z<4) or np.all(F*x+128*z<0) or np.all(F*x-128*z>0) or np.all(F*y+106*z<0) or np.all(F*y-106*z>0))
    frames=bytearray();stats=[];vertex_frames=bytearray();joint_stats=[];wheel_distance=0.;previous_pos=None;scenes=[];actors=[]
    motion=trajectory(N,road)
    camera_yaw=motion[0][0].yaw
    pose_lean=0.;pose_crouch=.5;pose_twist=0.;pose_dash=1.;pose_brake=0.;last_speed=0.
    for f in range(N):
        state,control=motion[f];s=state.z
        mat=ry(state.yaw);pos=np.array([state.x,0,state.z])
        delta=(state.yaw-camera_yaw+math.pi)%(2*math.pi)-math.pi
        camera_yaw+=delta*.20
        camera_mat=ry(camera_yaw)
        cp=pos-camera_mat@np.array([0,-145,250])
        forward=unit(camera_mat[:,2]-.22*camera_mat[:,1]);right=unit(np.cross([0,1,0],forward));up=np.cross(forward,right)
        view=np.array([right,up,forward]);k=0
        focus=pos+camera_mat@np.array([0,0,350])
        selected=sorted(range(32),key=lambda i:np.linalg.norm(chunks[i][1]-focus))[:4]
        selected.sort(key=lambda i:(view@(chunks[i][1]-cp))[2],reverse=True)
        poses=[(8+city.KINDS.index(city.tile_kind(i)),view,view@(chunks[i][1]-cp)) for i in selected]
        upcoming=motion[min(N-1,f+4)][1]
        turn=control.turn if abs(control.turn)>.01 else upcoming.turn*.4
        desired_lean=float(np.clip(turn*(.18 if state.speed<20 else .70)+state.lateral/110,-1,1))
        acceleration=state.speed-last_speed;last_speed=state.speed
        desired_brake=float(np.clip(-acceleration/80,0,1))
        desired_dash=float(np.clip(state.speed/400,0,1))
        desired_crouch=.28+.28*desired_dash+min(.22,abs(turn)*.18)+desired_brake*.18+min(.12,max(0,acceleration)/300)
        pose_lean+=(desired_lean-pose_lean)*.17
        pose_crouch+=(desired_crouch-pose_crouch)*.18
        pose_twist+=(float(np.clip(turn*.42,-.52,.52))-pose_twist)*.28
        pose_dash+=(desired_dash-pose_dash)*.22
        pose_brake+=(desired_brake-pose_brake)*.22
        body,feet,joints=body_pose(pose_lean,pose_crouch,pose_twist,pose_brake,pose_dash)
        vertex_frames+=compressed_vertices(body);joint_stats.append(joints)
        if previous_pos is not None:wheel_distance+=float(np.linalg.norm(pos-previous_pos))
        previous_pos=pos.copy()
        for foot,bank in zip(feet,(2,3)):
            wp=pos+mat@foot
            poses.append((bank,view@mat@ry(pose_twist*.12)@rx(wheel_distance/13.92),view@(wp-cp)))
        poses.append((1,view@mat,view@(pos-cp)))
        actors.append([(bank,view.T@matrix,view.T@position+cp) for bank,matrix,position in poses[-3:]])
        mode=(3 if state.speed<20 else 4) if abs(control.turn)>.2 else 1 if state.lateral<-20 else 2 if state.lateral>20 else 0
        scenes.append((poses[:4],view,cp,mode))
        stats.append({'f':f,'segment':k,'position':[state.x,state.z],'heading':state.yaw,'controls':vars(control),'banks':[p[0] for p in poses]})
    rival_positions=pursuit.positions(actors)
    occlusion_banks={};occlusion_bank=59;occlusion_offset=0
    enemy_yaw=motion[round(pursuit.phase(0))][0].yaw
    for f,(cityposes,view,cp,mode) in enumerate(scenes):
        e=round(pursuit.phase(f))%N;root=actors[e][-1][2];base_rot=actors[e][-1][1]
        eroot=rival_positions[f];erot=base_rot
        if pursuit.airborne_route(f):
            tangent=rival_positions[min(f+1,N-1)]-eroot
            target_yaw=math.atan2(tangent[0],tangent[2])
        else:target_yaw=motion[e][0].yaw
        enemy_yaw+=((target_yaw-enemy_yaw+math.pi)%(2*math.pi)-math.pi)*.35
        erot=ry(enemy_yaw)
        enemy=[]
        for bank,matrix,position in actors[e]:
            local=base_rot.T@(position-root)
            enemy.append((55 if bank==1 else bank,view@erot@base_rot.T@matrix,view@(eroot+erot@local-cp)))
        own=[(bank,view@matrix,view@(position-cp)) for bank,matrix,position in actors[f]]
        poses=cityposes+enemy+own
        rec=bytearray()
        for bank,matrix,position in poses:rec+=words((matrix*16384).flatten().tolist()+position.tolist())
        draw_banks=[255 if outside(bank,matrix,position) else bank for bank,matrix,position in poses]
        rec+=bytes(draw_banks)
        stats[f]['draw_banks']=draw_banks
        rec+=words([0,512,256,0])+struct.pack('<HH',212,1008 if f<52 else color256.HUD_ROWS[mode])
        rec+=struct.pack('<HB',0x4000+(f%32)*512,34+f//32)
        rec+=struct.pack('<HB',0x4000+(e%32)*512,34+e//32)
        compact=np.frombuffer(vertex_frames[e*512:e*512+148*3],dtype=np.uint8).reshape(-1,3).astype(int);compact[:,[0,2]]-=128
        cover,face_count=occlusion.make(cityposes,tile_models,banks,enemy,compact,car(2).v)
        if cover:
            if occlusion_offset+len(cover)>16384:occlusion_bank+=1;occlusion_offset=0
            assert occlusion_bank<64, 'occlusion stream exceeds spare ROM banks'
            if occlusion_bank not in occlusion_banks:occlusion_banks[occlusion_bank]=bytearray(16384)
            occlusion_banks[occlusion_bank][occlusion_offset:occlusion_offset+len(cover)]=cover
            rec+=struct.pack('<HB',0x4000+occlusion_offset,occlusion_bank)
            occlusion_offset+=len(cover)
        else:rec+=struct.pack('<HB',0,255)
        stats[f]['occlusion_faces']=face_count
        rec+=bytes(512-len(rec));frames+=rec
        stats[f]['rival_position']=eroot.tolist();stats[f]['rival_rooftop']=pursuit.airborne_route(f)
        stats[f]['rival_pose_frame']=e
        stats[f]['rival_route_phase']=pursuit.phase(f)
    texsky,atlas=textures.images(COLORS)
    texsky.save(OUT/'textured-sky.png');atlas.save(OUT/'texture-atlas.png')
    banks.extend(bytearray(frames[i:i+16384]) for i in range(0,len(frames),16384));banks.extend(bytearray(16384) for _ in range(64-len(banks)));assert len(banks)==64
    for i in range(0,len(vertex_frames),16384):banks[34+i//16384]=bytearray(vertex_frames[i:i+16384])
    banks[52]=bytearray(bitmap(texsky)[:16384]);banks[53]=bytearray(bitmap(texsky)[16384:])
    banks[54]=bytearray(bitmap(atlas));banks[55]=packmesh(body_pose()[0],robot=True,blue=True)
    assert len(vertex_frames)==N*512
    (OUT/'joints.json').write_text(json.dumps(joint_stats,indent=2))
    expanded,resources,texsky,atlas=color256.make(COLORS,sky,hud)
    for bank,data in resources.items():banks[bank]=data
    for bank,data in occlusion_banks.items():banks[bank]=data
    texsky.save(OUT/'textured-sky.png');atlas.save(OUT/'texture-atlas.png')
    (OUT/'palette256.json').write_text(json.dumps(expanded))
    pal=[]
    for rgb in expanded:
        r,g,b=[round(c/255*31) for c in rgb];pal.extend([r,g,b])
    (ROOT/'src/palette.inc').write_text('palette:\n .db '+','.join(map(str,pal))+'\n')
    subprocess.run([tool('sdasz80'),'-los',str(OUT/'player.rel'),str(ROOT/'src/player.asm')],cwd=ROOT/'src',check=True)
    subprocess.run([tool('sdldz80'),'-n','-i',str(OUT/'player'),str(OUT/'player.rel')],cwd=ROOT,check=True)
    for line in (OUT/'player.ihx').read_text().splitlines():
        r=bytes.fromhex(line[1:]);assert sum(r)%256==0
        if r[3]==0:
            n=r[0];a=int.from_bytes(r[1:3],'big')
            if a>=0xE800:assert a+n<=0xF000;a=a-0xE800+0x4100
            banks[0][a-0x4000:a-0x4000+n]=r[4:4+n]
    rom=b''.join(banks);assert len(rom)==1048576
    (OUT/'BULLRUSH.ROM').write_bytes(rom)
    report={'frames':N,'rom_bytes':len(rom),'chunks':[{'v':len(m.v),'f':len(m.f)} for m,o in chunks],'sha256':hashlib.sha256(rom).hexdigest()}
    (OUT/'buildings.json').write_text(json.dumps(city.buildings(),indent=2))
    (OUT/'motion.json').write_text(json.dumps(stats,indent=2))
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':build()
