import math
import numpy as np
from mesh import Mesh

class Model(Mesh):
 def face(self,ids,color):
  self.f.append((list(ids)+([ids[-1]] if len(ids)==3 else []),[0,0,0],color))
 def polygon(self,pts,color,twoside=False):
  i=len(self.v);self.v.extend(pts);ids=list(range(i,i+len(pts)));self.face(ids,color)
  if twoside:self.face(ids[::-1],color)
 def cube(self,x,y,z,sx,sy,sz,color):
  i=len(self.f);self.box(x,y,z,sx,sy,sz,color)
  for k in range(i,len(self.f)):
   ids,n,c=self.f[k];self.f[k]=(ids,[0,0,0],color)
 def orb(self,x,y,z,sx,sy,sz,color,n=6,lat=3):
  first=len(self.v);self.v.append((x,y+sy,z))
  for j in range(1,lat):
   a=math.pi*j/lat
   for k in range(n):
    t=2*math.pi*k/n;self.v.append((x+sx*math.sin(a)*math.cos(t),y+sy*math.cos(a),z+sz*math.sin(a)*math.sin(t)))
  last=len(self.v);self.v.append((x,y-sy,z))
  for k in range(n):
   self.face([first,first+1+(k+1)%n,first+1+k],color)
   for j in range(lat-2):
    a=first+1+j*n+k;b=first+1+j*n+(k+1)%n;self.face([a,b,b+n,a+n],color if k%4 else max(1,color-1))
   a=first+1+(lat-2)*n+k;b=first+1+(lat-2)*n+(k+1)%n;self.face([last,a,b],color)
 def head(self,x,y,z,sx,sy,sz,color,umin):
  first=len(self.f);self.orb(x,y,z,sx,sy,sz,color,n=8,lat=4)
  if not hasattr(self,'uv'):self.uv={}
  for i in range(first,len(self.f)):
   ids,n,c=self.f[i]
   if sum(self.v[j][2] for j in ids)/4<z:
    self.f[i]=(ids,n,128)
    self.uv[i]=sum(([max(umin,min(umin+63,round(umin+(self.v[j][0]-x+sx)*63/(2*sx)))),max(0,min(63,round((y+sy-self.v[j][1])*63/(2*sy))))] for j in ids),[])
 def cylinder(self,y0,y1,r,color,n=12):
  first=len(self.v)
  for y in [y0,y1]:
   for i in range(n):
    a=i*2*math.pi/n;self.v.append((r*math.cos(a),y,r*math.sin(a)))
  for i in range(n):self.face([first+i,first+(i+1)%n,first+n+(i+1)%n,first+n+i],color if i%3 else max(1,color-1))
  for i in range(1,n-1):
   self.face([first+n,first+n+i+1,first+n+i],14);self.face([first,first+i,first+i+1],12)
 def pack(self):
  uv=bytearray(len(self.f)*8)
  for i,coords in getattr(self,"uv",{}).items():uv[i*8:i*8+8]=bytes(coords)
  d=self.data()+uv;assert len(d)<16384
  return bytearray(d+bytes(16384-len(d))),{'vertices':len(self.v),'faces':len(self.f)}

def cat(seated=False):
 m=Model()
 m.orb(0,28,0,20,28,15,8)
 m.head(0,66,-2,30,27,24,8,128)
 for x in [-18,18]:
  m.polygon([(x-10,81,-9),(x+10,81,-9),(x,109,-4)],8,True)
  m.polygon([(x-5,85,-10),(x+5,85,-10),(x,101,-6)],11,True)

 if not seated:
  m.orb(-10,3,-7,10,7,15,13,n=4,lat=2);m.orb(10,3,-7,10,7,15,13,n=4,lat=2)
  m.polygon([(-18,48,13),(18,48,13),(34,4,42),(-32,6,43)],7,True)
  m.polygon([(-32,6,43),(34,4,42),(20,-4,48),(-16,-3,46)],7,True)
 return m

def rabbit():
 m=Model();m.orb(0,25,0,19,24,14,13);m.head(0,60,-2,27,26,23,13,192)
 for x in [-13,13]:
  m.orb(x,98,0,8,29,8,15,n=6,lat=3);m.cube(x,99,-7,5,35,2,11)
 m.orb(-10,3,-7,10,7,15,15,n=4,lat=2);m.orb(10,3,-7,10,7,15,15,n=4,lat=2)
 return m
