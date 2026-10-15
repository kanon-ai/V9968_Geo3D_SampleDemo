"""World-space motion model: autopilot supplies the same controls as future keys.
Units are world units / seconds / radians. No rendering or ROM packing here.
"""
from dataclasses import dataclass
import math
import numpy as np
@dataclass
class Controls:
    forward: float=1.0
    strafe: float=0.0
    turn: float=0.0
@dataclass
class State:
    x: float
    z: float
    yaw: float
    speed: float=519.0
    lateral: float=0.0

def step(s,c,dt):
    s.yaw+=max(-1,min(1,c.turn))*1.0*dt
    s.speed+=(max(0,min(1,c.forward))*519-s.speed)*min(1,dt*5)
    s.lateral+=(max(-1,min(1,c.strafe))*100-s.lateral)*min(1,dt*8)
    s.x+=(math.sin(s.yaw)*s.speed+math.cos(s.yaw)*s.lateral)*dt
    s.z+=(math.cos(s.yaw)*s.speed-math.sin(s.yaw)*s.lateral)*dt

def trajectory(n,road=None):
    route=np.array([(1920,960),(1920,1920),(2880,1920),(2880,1440),(3360,1440),(3360,960),(3840,960),(3840,1920),(4800,1920),(4800,960),(3840,960),(2880,960),(2880,1920),(1920,1920),(1920,960)],float)
    entries=route.copy();exits=route.copy();moving={i for i in range(1,len(route)-1) if i%2==1 and i not in (3,4,5)}
    for i in moving:
        incoming=route[i]-route[i-1];incoming/=np.linalg.norm(incoming)
        outgoing=route[i+1]-route[i];outgoing/=np.linalg.norm(outgoing)
        entries[i]-=incoming*125;exits[i]+=outgoing*125
    records=[]
    def emit(p,yaw,speed,strafe,turn):records.append((State(float(p[0]),float(p[1]),yaw,speed,strafe),Controls(min(1,speed/500),strafe/80,turn)))
    for i in range(len(route)-1):
        a=exits[i];b=entries[i+1];d=b-a;length=np.linalg.norm(d);direction=d/length;yaw=math.atan2(d[0],d[1]);side=np.array([direction[1],-direction[0]])
        steps=max(1,round(length/17))
        for j in range(steps):
            t=j/steps;slide=(0 if i in (3,4) else 100)*math.sin(t*2*math.pi)*math.sin(t*math.pi)
            start_stop=i>0 and i not in moving
            end_stop=(i+1)<len(route)-1 and (i+1) not in moving
            # Piecewise acceleration/deceleration at the ends of a straight.
            r=.18;den=1-r*.5*(start_stop+end_stop)
            if start_stop and t<r:progress=t*t/(2*r);velocity=t/r
            else:progress=t-(r*.5 if start_stop else 0);velocity=1.
            if end_stop and t>1-r:
                q=t-(1-r);progress-=q*q/(2*r);velocity=1-q/r
            progress/=den
            emit(a+d*progress+side*slide,yaw,500*velocity/den,35*math.cos(t*2*math.pi),0)
        k=i+1
        if k>=len(route)-1:continue
        out=route[k+1]-route[k];target=math.atan2(out[0],out[1]);delta=(target-yaw+math.pi)%(2*math.pi)-math.pi
        if k in moving:
            for j in range(18):
                t=j/18;p=(1-t)**2*entries[k]+2*(1-t)*t*route[k]+t*t*exits[k]
                tangent=2*(1-t)*(route[k]-entries[k])+2*t*(exits[k]-route[k])
                emit(p,math.atan2(tangent[0],tangent[1]),float(np.linalg.norm(tangent))*30/18,0,delta*.8)
        else:
            for j in range(20):
                t=j/19;e=t*t*(3-2*t)
                emit(route[k],yaw+delta*e,0,0,delta*6*t*(1-t))
    # Stretch the scripted sample count only; rendered video remains at actual runtime speed.
    indices=np.linspace(0,len(records)-1,n)
    result=[]
    for f in indices:
        a=records[int(f)];b=records[min(len(records)-1,int(f)+1)];t=f-int(f)
        yaw=a[0].yaw+((b[0].yaw-a[0].yaw+math.pi)%(2*math.pi)-math.pi)*t
        vals=[getattr(a[0],k)*(1-t)+getattr(b[0],k)*t for k in ('x','z','speed','lateral')]
        result.append((State(vals[0],vals[1],yaw,vals[2],vals[3]),Controls(*[getattr(a[1],k)*(1-t)+getattr(b[1],k)*t for k in ('forward','strafe','turn')])))
    return result
