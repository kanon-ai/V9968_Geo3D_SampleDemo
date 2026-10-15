"""Conservative whole-district rejection, in quantized Geo3D coordinates."""
import numpy as np

def visible_mask(hulls, record, first):
    m=np.array(record[:9],dtype=np.int64).reshape(3,3)
    pos=np.array(record[9:12],dtype=np.int64)
    step=np.array(record[12:15],dtype=np.int64)
    mask=0
    for j in range(5):
        v=np.rint(hulls[(first+j)%5].v).astype(np.int64)
        xyz=(v@m.T >> 14)+pos+j*step
        xyz=np.clip(xyz,-131071,131071)
        # Retain near-plane intersections; no speculative clipping rejection.
        keep=True
        if np.all(xyz[:,2]>=40):
            q=np.minimum(np.abs(xyz[:,:2])*190//xyz[:,2,None],32767)*np.sign(xyz[:,:2])
            x=np.clip(128+q[:,0],-32768,32767);y=np.clip(106-q[:,1],-32768,32767)
            keep=not (np.all(x < -2) or np.all(x > 257) or np.all(y < -2) or np.all(y > 213))
        if keep:mask |= 1 << (4-j)
    return mask
