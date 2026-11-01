"""Clip only near-plane-crossing faces for the airfield and mountain meshes.
Offline scene preparation; Geo3D still transforms and rasterizes every frame.
"""
import numpy as np
from mesh import Mesh

def clip_near(source,view,position,origin,uvbytes):
    out=Mesh();out.uv={};changed=False
    for fi,(ids,normal,base) in enumerate(source.f):
        # Remove the repeated fourth vertex on triangles.
        n=3 if ids[2]==ids[3] else 4
        world=np.array([source.v[i] for i in ids[:n]],float)
        cam=(view@(world+origin-position).T).T
        tex=np.array(list(uvbytes[fi*8:fi*8+8]),float).reshape(4,2)[:n]
        poly=[np.r_[a,b] for a,b in zip(cam,tex)]
        if np.min(cam[:,2])<8:
            changed=True
            # Near plane and screen rectangle. The extra pixel inset avoids
            # projecting rounded intersection vertices past the fixed-point edge.
            planes=[lambda p:p[2]-8,lambda p:p[0]+126*p[2]/170,
                    lambda p:126*p[2]/170-p[0],lambda p:p[1]+91*p[2]/170,
                    lambda p:91*p[2]/170-p[1]]
            for distance in planes:
                result=[]
                if not poly:break
                a=poly[-1];da=distance(a)
                for b in poly:
                    db=distance(b)
                    if (da>=0)!=(db>=0):result.append(a+(b-a)*(da/(da-db)))
                    if db>=0:result.append(b)
                    a=b;da=db
                poly=result
        if len(poly)<3:continue
        groups=[poly] if len(poly)<=4 else [[poly[0],poly[i],poly[i+1]] for i in range(1,len(poly)-1)]
        for g in groups:
            xyz=[(view.T@v[:3]+position-origin).tolist() for v in g]
            out.poly(xyz,normal,base)
            uv=[int(round(x)) for v in g for x in v[3:]]
            if len(g)==3:uv+=uv[-2:]
            out.uv[len(out.f)-1]=uv
    return out if changed else None
