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
 m.orb(-19,28,-5,8,17,8,13,n=4,lat=2);m.orb(19,28,-5,8,17,8,13,n=4,lat=2)
 if not seated:
  m.orb(-10,3,-7,10,7,15,13,n=4,lat=2);m.orb(10,3,-7,10,7,15,13,n=4,lat=2)
  m.polygon([(-18,48,13),(18,48,13),(34,4,42),(-32,6,43)],7,True)
  m.polygon([(-32,6,43),(34,4,42),(20,-4,48),(-16,-3,46)],7,True)
 return m

def rabbit():
 m=Model();m.orb(0,25,0,19,24,14,13);m.head(0,60,-2,27,26,23,13,192)
 for x in [-13,13]:
  m.orb(x,98,0,8,29,8,15,n=6,lat=3);m.cube(x,99,-7,5,35,2,11)
 m.orb(-15,30,-13,8,9,8,15,n=4,lat=2);m.orb(15,30,-13,8,9,8,15,n=4,lat=2)
 return m

def can():
 m=Model();m.cylinder(-64,0,39,6)
 # Silver rims and engine skirt.
 m.cylinder(-6,0,42,12);m.cylinder(-66,-60,41,12)
 m.cube(0,-34,-39,49,31,2,13)
 # Raised paw emblem on the label.
 m.orb(0,-39,-42,10,8,2,8,n=4,lat=2)
 for x,y in [(-13,-29),(-5,-24),(5,-24),(13,-29)]:m.orb(x,y,-42,4,4,2,8,n=4,lat=2)
 # Printed texture label facing the camera, rendered through Geo3D LRMM.
 m.uv={}
 for pts,coords in [([(-32,-10,-40),(-32,-56,-40),(32,-56,-40),(32,-10,-40)],[0,0,0,63,127,63,127,0]),([(32,-10,-40),(32,-56,-40),(-32,-56,-40),(-32,-10,-40)],[127,0,127,63,0,63,0,0])]:
  i=len(m.f);m.polygon(pts,128);m.uv[i]=coords
 m.cube(0,2,0,17,2,23,12)
 return m

def rocket(power=0):
 m=Model();n=10;first=len(m.v)
 rings=[(-123,5),(-100,25),(-65,36),(65,36),(96,29)]
 for x,r in rings:
  for k in range(n):
   a=k*2*math.pi/n;m.v.append((x,r*math.cos(a),r*math.sin(a)))
 for j in range(len(rings)-1):
  for k in range(n):
   a=j*n+k;b=j*n+(k+1)%n;m.face([a,b,b+n,a+n],[4,4,3,3,2,2,3,3,4,5][k])
 for k in range(1,n-1):m.face([40,40+k,40+k+1],12)
 # Rear nozzle: local +X is aft; the nose points toward -X.
 start=len(m.v)
 for x,r in [(96,22),(113,27)]:
  for k in range(8):
   a=k*math.pi/4;m.v.append((x,r*math.cos(a),r*math.sin(a)))
 for k in range(8):
  a=start+k;b=start+(k+1)%8;m.face([a,b,b+8,a+8],12 if k%2 else 2)
 center=len(m.v);m.v.append((114,0,0))
 for k in range(8):m.face([center,start+8+k,start+8+(k+1)%8],1)
 if power:
  for radius,length,color in [(23,155*power,8),(13,105*power,9)]:
   first=len(m.v)
   for k in range(6):
    a=k*math.pi/3;m.v.append((115,radius*math.cos(a),radius*math.sin(a)))
   tip=len(m.v);m.v.append((115+length,0,0))
   for k in range(6):
    ids=[first+k,tip,first+(k+1)%6];m.face(ids,color);m.face(ids[::-1],color)
 # Four playful swept fins.
 for sign in [-1,1]:
  m.polygon([(48,0,sign*25),(88,0,sign*75),(105,0,sign*29)],4,True)
  m.polygon([(48,sign*25,0),(89,sign*75,0),(104,sign*29,0)],3,True)
 # Cockpit rims and black openings on the upper hull.
 for x in [-40,35]:
  for r,y,col in [(25,38,4),(19,39,1)]:
   pts=[(x+r*math.cos(k*2*math.pi/8),y,r*.7*math.sin(k*2*math.pi/8)) for k in range(8)]
   for k in range(1,7):m.polygon([pts[0],pts[k],pts[k+1]],col,True)
 # Side portholes.
 for x in [-32,12,56]:m.orb(x,0,-35,9,9,2,4,n=6,lat=2)
 return m

def flame():
 m=Model()
 for r,end,col in [(26,-175,8),(17,-130,9),(9,-85,15)]:
  for k in range(6):
   a=k*math.pi/3;b=(k+1)*math.pi/3
   m.polygon([(r*math.cos(a),0,r*math.sin(a)),(0,end,0),(r*math.cos(b),0,r*math.sin(b))],col,True)
 return m

def clouds():
 m=Model()
 for x,y,z,scale in [(-220,0,200,1),(230,70,120,.8),(-70,-200,0,1.1),(120,210,100,.9)]:
  m.orb(x,y,z,110*scale,40*scale,55*scale,14,n=8,lat=3)
 return m

def streaks():
 m=Model();rng=np.random.default_rng(23)
 for i in range(20):
  a=i*2*math.pi/20;r=180+float(rng.random())*90;x=r*math.cos(a);y=r*math.sin(a);z=float(rng.random())*500
  m.polygon([(x-1,y,z),(x+1,y,z),(x+1,y-175,z),(x-1,y-175,z)],5 if i%3 else 15,True)
 return m


def cloud_tunnel():
 m=Model()
 for i in range(6):
  a=i*math.pi/3;m.orb(245*math.cos(a),210*math.sin(a),40*math.sin(a*2),160,110,70,14 if i%2 else 15,n=6,lat=2)
 return m


def beacon():
 m=Model()
 m.polygon([(-3,3,-48),(3,3,-48),(3,138,-48),(-3,138,-48)],11,True)
 for y in range(12,125,16):m.cube(0,y,0,5,12,5,9)
 m.cube(0,140,0,34,4,4,9)
 for i in range(12):
  a=i*math.pi/6;b=(i+1)*math.pi/6
  m.polygon([(22*math.cos(a),140,22*math.sin(a)),(26*math.cos(a),140,26*math.sin(a)),(26*math.cos(b),140,26*math.sin(b)),(22*math.cos(b),140,22*math.sin(b))],9,True)
 return m


def harbor_backdrop():
 m=Model()
 # Sky, pale horizon and sea, deliberately without location-specific landmarks.
 for y0,y1,col in [(1400,240,2),(240,90,3),(90,0,5),(0,-1400,3)]:
  m.polygon([(-1800,y0,6000),(1800,y0,6000),(1800,y1,6000),(-1800,y1,6000)],col,True)
 for j in range(8):
  y=-70-j*70
  m.polygon([(-900+j*60,y,5990),(650-j*35,y,5990),(650-j*35,y-5,5990),(-900+j*60,y-5,5990)],5,True)
 return m

def harbor_distance():
 m=Model()
 # Warehouse silhouettes, dock cranes and a small moored cargo boat.
 for x,h,w in [(-580,120,150),(-390,75,170),(400,110,170),(590,140,130)]:
  m.cube(x,-45+h/2,4300,w,h,90,12)
  m.cube(x,h-43,4300,w+14,12,110,2)
 for x in [-360,480]:
  m.cube(x,95,4200,12,220,12,8);m.cube(x-65,200,4200,160,10,12,8)
  m.cube(x-120,145,4200,3,110,3,2)
 m.cube(-70,-28,4600,210,35,100,2);m.cube(-20,10,4600,75,45,70,14)
 m.cube(-20,40,4600,45,12,60,3)
 return m

def harbor_quay():
 m=Model()
 m.cube(0,-175,3200,1600,70,1800,12)
 m.cube(0,-140,3890,1600,8,30,13)
 for x in [-400,-210,230,410]:
  m.cube(x,-123,3750,24,28,24,2)
 for x in [-480,480]:
  m.cube(x,-12,3500,8,260,8,2);m.cube(x,122,3500,38,16,18,9)
 return m
