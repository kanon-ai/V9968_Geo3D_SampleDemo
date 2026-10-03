"""Continuous, grounded two-bone rig. +Y is up, +Z is forward.

This module builds the existing armor around articulated joints, not a walk
cycle. Roller boots stay on the ground; shoulders, elbows, hips, knees and
ankles have connected endpoints. Pose generation is offline in this demo.
"""
import math
import numpy as np
from mesh import Mesh


def unit(v):
    return np.asarray(v, float) / max(float(np.linalg.norm(v)), 1e-9)


def rx(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])


def ry(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])


def rz(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def knee_between(hip,ankle,upper=34.,lower=34.):
    axis=ankle-hip;distance=float(np.linalg.norm(axis))
    assert abs(upper-lower)+.01<distance<upper+lower-.01, distance
    axis/=distance
    pole=np.array([0.,0.,1.]);pole=unit(pole-axis*np.dot(pole,axis))
    along=(upper*upper-lower*lower+distance*distance)/(2*distance)
    return hip+axis*along+pole*math.sqrt(max(0,upper*upper-along*along))


def body_pose(lean=0.,crouch=.5,twist=0.,brake=0.,dash=1.):
    m=Mesh();joints={}
    def armor(center,size,color,rotation=None,top=1.,bottom=1.,sweep=0.):
        rotation=np.eye(3) if rotation is None else rotation
        first=len(m.v);face_start=len(m.f)
        m.box(0,0,0,*size,color)
        for i in range(first,len(m.v)):
            p=np.array(m.v[i]);upper=p[1]>0
            p[0]*=top if upper else bottom
            if upper:p[2]+=sweep
            m.v[i]=tuple(rotation@p+center)
        for i in range(face_start,len(m.f)):
            ids,normal,c=m.f[i]
            # Restrained local facet shading; no texture mapping.
            c=max(1,min(15,c+(1 if normal[1]>0 else -1 if normal[0]<0 else 0)))
            m.f[i]=(ids,[0,0,0],c)
    def limb(a,b,width,depth,color,top=1.,bottom=1.):
        up=unit(a-b);right=unit(np.cross(up,[0,0,1]));front=np.cross(right,up)
        armor((a+b)*.5,(width,float(np.linalg.norm(a-b)),depth),color,np.column_stack((right,up,front)),top,bottom)

    crouch=float(np.clip(crouch,0,1));lean=float(np.clip(lean,-1,1))
    # The pelvis moves over the supporting foot, rather than rotating the model
    # about its origin. A slight fore/aft split makes the planted stance legible.
    pelvis=np.array([lean*11.,78-15*crouch,-6+4*dash-5*brake])
    pelvis_rot=ry(twist*.22)@rz(-lean*.11)
    torso_rot=ry(twist*.75)@rz(-lean*.27)@rx(.08+.29*dash+.14*crouch-.24*brake)
    chest=pelvis+torso_rot@np.array([0,27,2])
    armor(pelvis,(29,12,22),3,pelvis_rot,.7,1.)
    armor(pelvis+torso_rot@np.array([0,12,0]),(17,16,18),2,torso_rot,.8,1.)
    armor(chest,(45,29,29),5,torso_rot,1.08,.48,6)
    neck=pelvis+torso_rot@np.array([0,47,0])
    headrot=ry(twist)@rz(-lean*.08)@rx(.07)
    armor(neck+np.array([0,7,1]),(18,15,20),4,headrot,.65,1.,4)
    # A four-vertex visor keeps the body vertex stream below 512 bytes.
    v=[(-7,0,12),(7,0,12),(6,4,12),(-6,4,12)]
    m.poly([tuple(headrot@np.array(p)+neck+[0,7,1]) for p in v],[0,0,0],8)
    feet=[]
    for side in (-1,1):
        shoulder=pelvis+torso_rot@np.array([side*29,38,0])
        elbow=shoulder+torso_rot@np.array([side*(5+abs(lean)*7),-20+side*lean*5,-11-8*dash+side*lean*5])
        # Forearms sweep forward about real elbows: hands are not hanging down.
        wrist=elbow+torso_rot@np.array([-side*3,7+9*brake-side*lean*6,20+4*dash])
        armor(shoulder,(20,18,25),5,torso_rot,1.16,.5,5)
        limb(shoulder,elbow,10,12,2)
        limb(elbow,wrist,14,17,4,.65,1.)
        pack=pelvis+torso_rot@np.array([side*12,27,-18])
        armor(pack,(11,27,12),3,torso_rot,.5,1.,-5)
        foot=np.array([side*22.,13.92,side*(5+11*dash)])
        ankle=foot+np.array([0,11,0]);hip=pelvis+pelvis_rot@np.array([side*12,0,0])
        knee=knee_between(hip,ankle)
        limb(hip,knee,13,17,4,.75,1.)
        limb(knee,ankle,16,20,5,.6,1.)
        armor(foot+[0,7,4],(23,12,38),4,ry(twist*.12),.72,1.,-3)
        joints[str(side)]={'hip':hip.tolist(),'knee':knee.tolist(),'ankle':ankle.tolist(),'shoulder':shoulder.tolist(),'elbow':elbow.tolist(),'wrist':wrist.tolist()}
        feet.append(foot)
    m.v=[tuple(round(float(x)) for x in v) for v in m.v]
    assert len(m.v)<=170 and len(m.f)<=255,(len(m.v),len(m.f))
    return m,feet,{'pelvis':pelvis.tolist(),'legs':joints,'dash':dash,'crouch':crouch,'lean':lean,'twist':twist,'brake':brake}


def compressed_vertices(mesh):
    a=np.array(mesh.v,dtype=int)+[128,0,128]
    assert a.min()>=0 and a.max()<=255,(a.min(),a.max())
    data=a.astype(np.uint8).tobytes()
    return data+bytes(512-len(data))
