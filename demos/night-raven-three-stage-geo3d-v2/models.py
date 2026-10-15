"""Distinct original solid meshes: interceptor, orbital drone, heavy lancer."""
import numpy as np
from mesh import Mesh

def wedge(m,points,base=1):
    start=len(m.v);m.v.extend(points);center=np.mean(points,axis=0)
    # Four point tetrahedron, outward-facing triangles.
    for ids in ((0,1,2),(0,3,1),(0,2,3),(1,3,2)):
        p=np.array([points[i] for i in ids],float)
        normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal)
        ids=list(ids)
        if np.dot(normal,p.mean(axis=0)-center)<0:normal=-normal;ids.reverse()
        indices=[start+i for i in ids];indices.append(indices[-1])
        m.f.append((indices,normal.tolist(),base))

def interceptor():
    m=Mesh()
    wedge(m,[(-14,-5,-60),(14,-5,-60),(0,18,-30),(0,0,115)],1)
    for s in (-1,1):
        wedge(m,[(s*10,0,40),(s*112,-3,-68),(s*30,8,-30),(s*14,-6,-62)],1)
        wedge(m,[(s*16,0,-45),(s*29,40,-65),(s*20,5,-5),(s*12,5,-48)],8)
        m.box(s*13,-2,-40,15,14,35,8)
    return m

def drone():
    m=Mesh()
    wedge(m,[(0,32,0),(-40,0,25),(40,0,25),(0,0,-55)],8)
    wedge(m,[(0,-28,0),(-40,0,25),(40,0,25),(0,0,-55)],1)
    for s in (-1,1):
        m.box(s*83,0,0,22,46,100,1)
        m.box(s*45,0,0,70,9,14,8)
        wedge(m,[(s*70,14,48),(s*97,0,65),(s*83,-14,48),(s*83,0,100)],8)
    return m

def heavy():
    m=Mesh()
    m.box(0,0,-5,58,40,125,1)
    wedge(m,[(-29,20,58),(29,20,58),(0,-20,58),(0,0,145)],1)
    for s in (-1,1):
        m.box(s*83,-5,-20,32,32,140,1)
        wedge(m,[(s*20,12,40),(s*145,-8,-84),(s*85,10,-10),(s*25,-14,-58)],8)
        m.box(s*110,-4,4,18,18,94,8)
    m.box(0,25,10,32,14,35,8)
    return m

def missile():
    m=Mesh()
    wedge(m,[(-5,-4,-17),(5,-4,-17),(0,5,-17),(0,0,30)],1)
    for s in (-1,1):wedge(m,[(s*3,0,-8),(s*16,0,-20),(s*3,4,-20),(s*3,-4,-20)],8)
    return m

def capsule():
    m=Mesh()
    wedge(m,[(0,42,0),(-30,0,-22),(30,0,-22),(0,0,35)],8)
    wedge(m,[(0,-42,0),(-30,0,-22),(30,0,-22),(0,0,35)],8)
    return m
