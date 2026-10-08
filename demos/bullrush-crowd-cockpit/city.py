"""Editable map / geometric tiles. Material slots are reserved, not textured."""
from pathlib import Path
import json
import numpy as np
from mesh import Mesh

ROOT=Path(__file__).resolve().parent
MAP=json.loads((ROOT/'city.json').read_text())
KINDS=list(MAP['districts'])
def tile_kind(index):return MAP['rows_south_to_north'][index//8][index%8]
def origin(index):return np.array([(index%8)*960.,0.,(index//8)*960.])

def tile_mesh(kind):
    spec=MAP['districts'][kind];m=Mesh()
    def face(points,c):
        p=np.array(points,float)
        if np.cross(p[1]-p[0],p[2]-p[0])[1]<0:p=p[::-1]
        m.poly(p.tolist(),[0,0,0],c)
    def panel(p,c,normal):
        points=np.array(p,float)
        if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),normal)<0:p=p[::-1]
        m.poly(p,[0,0,0],c)
    face([[-480,0,-480],[480,0,-480],[480,0,480],[-480,0,480]],2)
    for x in (-330,330):
        for z in (-330,330):
            if kind=='plaza':
                face([[x-140,1,z-140],[x+140,1,z-140],[x+140,1,z+140],[x-140,1,z+140]],4)
                # Low recessed garden and low bench: an open space, not a tower.
                face([[x-80,2,z-80],[x+80,2,z-80],[x+80,2,z+80],[x-80,2,z+80]],9)
                m.box(x,8,z+105,90,16,15,3)
                continue
            h=spec['height']+(30 if x*z>0 else 0);w=spec['width'];r=w/2
            face([[x-r-10,2,z-r-10],[x+r+10,2,z-r-10],[x+r+10,2,z+r+10],[x-r-10,2,z+r+10]],4)
            m.box(x,h/2+3,z,w,h,w,spec['wall'])
            m.box(x,h+14,z,w*.75,24,w*.75,spec['roof'])
            # Large panels plus solid vertical border. No coplanar z-fighting.
            for flip in (-1,1):
                y=h*.25;top=h*.76;xx=x+flip*(r+1);zz=z+flip*(r+1);v=r-24
                panel([[xx,y,z-v],[xx,top,z-v],[xx,top,z+v],[xx,y,z+v]],spec['glass'],[flip,0,0])
                panel([[x-v,y,zz],[x+v,y,zz],[x+v,top,zz],[x-v,top,zz]],spec['glass'],[0,0,flip])
            if kind=='retail':
                # Low shop canopy / sign band is visible while dashing past.
                m.box(x,75,z,w+26,12,w+26,spec['roof'])
                m.box(x,88,z,w*.6,12,w+4,8)
            else:
                m.box(x,h+37,z,w*.42,20,w*.5,spec['wall'])
    for a in (-410,-270,270,410):
        face([[-3,1,a-35],[3,1,a-35],[3,1,a+35],[-3,1,a+35]],8)
        face([[a-35,1,-3],[a+35,1,-3],[a+35,1,3],[a-35,1,3]],8)
    # Deduplicate vertices but preserve original material colors on flat panels.
    mapping={};vertices=[];remap=[]
    for v in m.v:
        key=tuple(round(x) for x in v)
        if key not in mapping:mapping[key]=len(vertices);vertices.append(key)
        remap.append(mapping[key])
    m.v=vertices
    m.f=[([remap[i] for i in ids],[0,0,0],max(1,min(15,c+(1 if normal[1]>0 else -1 if normal[0]<0 else 0)))) for ids,normal,c in m.f]
    assert len(m.v)<=255 and len(m.f)<=255,(kind,len(m.v),len(m.f))
    return m

def buildings():
    result=[]
    for i in range(32):
        kind=tile_kind(i);s=MAP['districts'][kind]
        if not s['height']:continue
        for x in (-330,330):
            for z in (-330,330):
                result.append({'tile':i,'kind':kind,'position':(origin(i)+[x,0,z]).tolist(),'half_size':[s['width']/2]*2,'height':s['height']+(30 if x*z>0 else 0),'material_slots':['wall','glass','roof']+(['shop_sign'] if kind=='retail' else [])})
    return result
