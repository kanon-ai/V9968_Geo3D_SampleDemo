import math
import numpy as np
from mesh import Mesh

def mochi_rabbit(phase):
 m=Mesh()
 def box(x,y,z,sx,sy,sz,color):
  start=len(m.f);m.box(x,y,z,sx,sy,sz,color)
  for i in range(start,len(m.f)):
   ids,n,c=m.f[i];m.f[i]=(ids,[0,0,0],c)
 def ball(x,y,z,sx,sy,sz,color):
  # Compact octahedral rounded silhouette, shared vertices.
  start=len(m.v)
  pts=[(x,y+sy,z),(x,y-sy,z),(x-sx,y,z),(x,y,z-sz),(x+sx,y,z),(x,y,z+sz)]
  m.v.extend(pts)
  for pole in [0,1]:
   for a,b in [(2,3),(3,4),(4,5),(5,2)]:
    ids=[start+pole,start+a,start+b];p=np.array([m.v[j] for j in ids]);normal=np.cross(p[1]-p[0],p[2]-p[0])
    if np.dot(normal,p.mean(axis=0)-[x,y,z])<0:ids.reverse()
    m.f.append((ids+[ids[-1]],[0,0,0],color))
 # Rabbit faces screen-right toward the mortar, with ears and a cotton tail.
 box(-25,5,0,25,9,20,15);box(-21,7,-12,23,9,17,15)
 ball(-29,26,0,19,26,17,14);ball(-42,19,8,10,10,10,15)
 ball(-22,53,0,17,17,15,15)
 box(-31,77,0,7,30,8,15);box(-17,78,0,7,33,8,15)
 box(-31,77,-4.5,3,23,1,9);box(-17,78,-4.5,3,26,1,9)
 box(-12,57,-12,4,4,3,0);ball(-5,48,-2,9,7,9,15)
 # Mortar: dark hollow top, golden wooden body and a white mochi mound.
 box(28,12,0,33,24,29,9);box(28,24,0,36,4,32,9)
 box(28,26,0,25,1,21,0);ball(28,28,-1,10,4,8,15)
 # Pivot the mallet: long anticipation, rapid downstroke, brief impact.
 swing=(.5-.5*math.cos(2*math.pi*phase))
 angle=1.75*swing
 pivot=np.array([-9.,41.,-8.]);rot=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
 start=len(m.v);box(15,0,0,45,5,5,9);box(37,0,0,13,22,15,9)
 for i in range(start,len(m.v)):m.v[i]=tuple(pivot+rot@np.array(m.v[i]))
 ball(-7,42,-9,7,7,7,15)
 # Tiny flour puffs at the strike.
 if swing<.12:
  ball(44,32+35*swing,-5,4,4,4,15);ball(16,34+50*swing,-7,3,3,3,15)
 data=m.data()+bytes(len(m.f)*8)
 assert len(data)<16384
 return bytearray(data+bytes(16384-len(data))),{'vertices':len(m.v),'faces':len(m.f)}
