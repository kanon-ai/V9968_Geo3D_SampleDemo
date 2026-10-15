"""Conservative foreground-face pass for the authored demo, rendered by Geo3D.

Only faces whose plane places the entire rival behind them qualify. Source
geometry and UVs are retained; this is not a bitmap mask or a Z-buffer.
"""
import struct
import numpy as np
from mesh import Mesh

def make(cityposes,models,banks,enemy,body,wheel):
    robot=np.concatenate([(matrix@np.array(body if bank==55 else wheel).T).T+pos for bank,matrix,pos in enemy])
    if robot[:,2].min()<5:return b'',0
    projected=robot[:,:2]*170/robot[:,2,None]
    low=projected.min(axis=0);high=projected.max(axis=0)
    mesh=Mesh();uvs=bytearray();mapping={};source_count=0
    for bank,matrix,pos in cityposes:
        m=models[bank-8];points=(matrix@np.array(m.v).T).T+pos
        vb,fb=struct.unpack_from('<HH',banks[bank],2)
        for j,(ids,n,color) in enumerate(m.f):
            face=points[ids];normal=np.cross(face[1]-face[0],face[2]-face[0])
            if np.linalg.norm(normal)<1e-6 or np.dot(normal,-face[0])<=0:continue
            # Do not paint over a limb which is actually on the camera side.
            if np.max((robot-face[0])@normal)>-.01:continue
            uv=np.frombuffer(banks[bank][6+vb+fb+j*8:6+vb+fb+(j+1)*8],dtype=np.uint8).reshape(4,2)
            polygon=[np.concatenate((v,t.astype(float))) for v,t in zip(face,uv)]
            clipped=[]
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                ia=a[2]>=5;ib=b[2]>=5
                if ia:clipped.append(a)
                if ia!=ib:clipped.append(a+(b-a)*((5-a[2])/(b[2]-a[2])))
            if len(clipped)<3:continue
            v=np.array(clipped);q=v[:,:2]*170/v[:,2,None]
            if np.any(q.max(axis=0)<low) or np.any(q.min(axis=0)>high):continue
            polygons=[clipped] if len(clipped)<=4 else [[clipped[0],clipped[k],clipped[k+1]] for k in range(1,len(clipped)-1)]
            source_count+=1
            for poly in polygons:
                if len(poly)==3:poly=poly+[poly[-1]]
                indices=[]
                for vertex in poly:
                    key=tuple(np.round(vertex[:3]).astype(int))
                    if key not in mapping:mapping[key]=len(mesh.v);mesh.v.append(key)
                    indices.append(mapping[key]);uvs.extend(bytes(np.clip(np.round(vertex[3:]),0,255).astype('uint8')))
                mesh.f.append((indices,[0,0,0],color))
    if not mesh.f:return b'',0
    return mesh.data()+uvs,source_count
