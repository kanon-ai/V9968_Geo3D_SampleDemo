"""Flight state is independent of scene meshes and renderer packet encoding.
The current ROM uses sampled autopilot states. Future controls must supply these
states at runtime; no interactive flight dynamics are implemented yet.
"""
from dataclasses import dataclass
import math
import numpy as np
START=1500.;END=27360.;RADIUS=1100.
STRAIGHT=END-START;CIRCUIT=2*STRAIGHT+2*math.pi*RADIUS
@dataclass
class FlightState:
    position: np.ndarray
    direction: np.ndarray
    camera_direction: np.ndarray
    bank: float
    route_s: float
    stage: str

def unit(v):return v/max(np.linalg.norm(v),1e-9)
def route(phase):
    d=(phase%1)*CIRCUIT
    if d<STRAIGHT:return START+d,0.,'outbound',0.
    d-=STRAIGHT
    if d<math.pi*RADIUS:
        a=d/RADIUS;return END+RADIUS*math.sin(a),-1800+1800*math.cos(a),'kyoto_turn',a
    d-=math.pi*RADIUS
    if d<STRAIGHT:return END-d,-3600.,'return',0.
    a=(d-STRAIGHT)/RADIUS
    return START-RADIUS*math.sin(a),-1800-1800*math.cos(a),'tokyo_turn',a

def altitude(s):return 550+110*math.exp(-((s-8500)/3300)**2)
def sample_autopilot(phase,point):
    def pos(t):
        s,x,stage,a=route(t);return point(s,x,altitude(s))
    s,x,stage,a=route(phase);p=pos(phase)
    fw=unit(pos(phase+.00003)-pos(phase-.00003))
    old=unit(pos(phase-.00003)-pos(phase-.00009));new=unit(pos(phase+.00009)-pos(phase+.00003))
    yaw_delta=math.atan2(np.cross(old,new)[1],np.dot(old,new))
    bank=max(-.22,min(.22,yaw_delta*24))
    camera=unit(fw+np.array([0,-.16,0]))
    if stage=='outbound':
        w=.72*math.exp(-((s-6900)/1700)**2)
        camera=unit(camera*(1-w)+unit(point(8160,1750,750)-p)*w)
    elif stage=='return':
        w=.58*math.exp(-((s-10500)/2000)**2)
        camera=unit(camera*(1-w)+unit(point(8160,1750,750)-p)*w)
    elif stage=='kyoto_turn':
        w=.95*math.sin(a)
        camera=unit(camera*(1-w)+unit(point(END,-RADIUS,240)-p)*w)
    return FlightState(p,fw,camera,bank,s,stage)



def sample_departure(frame,point):
    def pos(f):
        t=max(0,min(1,f/256))
        end_speed=CIRCUIT/4096
        start_speed=2*(START+800)/256-end_speed
        s=-800+start_speed*256*t+(end_speed-start_speed)*128*t*t
        u=max(0,min(1,(t-.25)/.75))
        y=20+(altitude(START)-20)*(u*u*(3-2*u))
        return point(s,0,y),s
    p,s=pos(frame);before,_=pos(frame-.1);after,_=pos(frame+.1)
    fw=unit(after-before)
    # Smoothly level into the existing route without changing its states.
    target=sample_autopilot(0,point)
    t=frame/256;w=t*t*(3-2*t)
    camera=unit(fw+np.array([0,-(.08+.08*w),0]))
    if t>.85:
        u=(t-.85)/.15;u=u*u*(3-2*u)
        camera=unit(camera*(1-u)+target.camera_direction*u)
    return FlightState(p,fw,camera,0.,s,'departure')
