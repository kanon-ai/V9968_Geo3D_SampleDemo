"""Demo pursuit timing. Ground speed advantage is shared with future controls.

No catch-up teleport or distance clamp: the rival loses its lead on roads and
regains route progress at explicit rooftop shortcuts. This is authored demo
choreography, not runtime AI or collision resolution.
"""
import numpy as np

PLAYER_SPEED=519.0
PLAYER_ADVANTAGE=1.08
RIVAL_SPEED=PLAYER_SPEED/PLAYER_ADVANTAGE
SHORTCUTS=((90,156),(230,300))

def phase(frame):
    if frame<90:return 60+frame/PLAYER_ADVANTAGE
    if frame<156:return (60+90/PLAYER_ADVANTAGE)+(frame-90)*(172-(60+90/PLAYER_ADVANTAGE))/66
    if frame<230:return 172+(frame-156)/PLAYER_ADVANTAGE
    if frame<300:return (172+74/PLAYER_ADVANTAGE)+(frame-230)*(320-(172+74/PLAYER_ADVANTAGE))/70
    return 320+(frame-300)/PLAYER_ADVANTAGE

def sample(actors,value):
    a=int(value)%len(actors);b=(a+1)%len(actors);t=value-int(value)
    return actors[a][-1][2]*(1-t)+actors[b][-1][2]*t

def jump(a,b,t,height):
    p=a*(1-t)+b*t;p[1]+=height*4*t*(1-t)
    return p

def positions(actors):
    points=[]
    for f in range(len(actors)):
        p=sample(actors,phase(f))
        if 90<=f<112:
            p=jump(sample(actors,phase(90)),np.array([3180.,156.,1290.]),(f-90)/22,65)
        elif 112<=f<132:p=np.array([3180+3*(f-112),156.,1290.])
        elif 132<=f<156:
            p=jump(np.array([3240.,156.,1290.]),sample(actors,phase(156)),(f-132)/24,60)
        elif 230<=f<248:
            p=jump(sample(actors,phase(230)),np.array([4150.,126.,1620.]),(f-230)/18,65)
        elif 248<=f<254:p=np.array([4150+(f-248)*40/6,126.,1620.])
        elif 254<=f<270:
            p=jump(np.array([4190.,126.,1620.]),np.array([4450.,156.,1620.]),(f-254)/16,75)
        elif 270<=f<276:p=np.array([4450+(f-270)*40/6,156.,1620.])
        elif 276<=f<300:
            p=jump(np.array([4490.,156.,1620.]),sample(actors,phase(300)),(f-276)/24,70)
        points.append(p)
    return points

def airborne_route(frame):return any(a<=frame<b for a,b in SHORTCUTS)
