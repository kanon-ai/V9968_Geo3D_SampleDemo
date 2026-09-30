"""Five contiguous, deliberately unequal hull districts, in world-space order."""
import math
from mesh import Mesh

def districts():
    result=[]
    for kind in range(5):
        m=Mesh()
        m.box(-690,0,160,100,1040,320,1)
        if kind==0: # Solid sloped armour, no opening.
            m.box(-495,60,160,330,710,320,1)
            m.box(-365,160,135,95,280,250,1)
            m.box(-407,-305,160,85,70,300,1)
            m.box(-348,135,130,26,8,235,1)
        elif kind==1: # Rounded power conduit / machinery housing.
            m.box(-520,0,160,240,880,320,1)
            first=len(m.v)
            for z in (0,320):
                for k in range(8):
                    a=k*math.tau/8
                    m.v.append((-430+125*math.cos(a),85+205*math.sin(a),z))
            for k in range(8):
                a=(k+.5)*math.tau/8
                m.f.append(([first+k,first+(k+1)%8,first+8+(k+1)%8,first+8+k],[math.cos(a),math.sin(a),0],1))
            for y in (-320,-270):m.box(-373,y,160,90,28,315,1)
        elif kind==2: # The single deep hangar in the five-district run.
            m.box(-480,-140,160,320,30,280,1)
            m.box(-480,140,160,320,30,280,1)
            for z in (12,308):m.box(-480,0,z,320,280,24,1)
            for y in (-360,360):m.box(-500,y,160,310,380,320,1)
            for z in (72,247):m.box(-470,-120,z,285,8,7,10)
            for x,z in ((-545,95),(-430,185)):
                m.box(x,-99,z,65,16,18,1)
                m.box(x-8,-98,z,20,7,55,1)
                m.box(x-30,-97,z,12,20,27,10)
            for z in (44,276):m.box(-330,158,z,8,8,8,11)
        elif kind==3: # Recessed pipework, deliberately asymmetrical.
            m.box(-565,0,160,170,990,320,1)
            m.box(-442,335,160,145,220,320,1)
            m.box(-480,-360,160,190,200,320,1)
            for y,x in ((-180,-425),(-105,-450),(0,-417),(110,-460)):
                m.box(x,y,160,45,24,320,1)
            m.box(-407,45,220,105,330,28,1)
        else: # Broad overhanging equipment block and a small turret.
            m.box(-535,0,160,230,920,320,1)
            m.box(-387,215,150,220,260,265,1)
            m.box(-323,215,150,130,170,200,1)
            m.box(-384,-190,110,90,125,140,1)
            m.box(-343,-190,180,26,22,170,1)
            m.box(-400,-325,160,60,30,320,1)
        # Subdue wall shading only; ships, HUD and energy effects retain contrast.
        m.f=[(ids,[v*.48 for v in normal],2 if base==1 and i>=6 else base)
             for i,(ids,normal,base) in enumerate(m.f)]
        # Low-contrast plate inlays on the actual exposed surfaces, not floating
        # screen-space noise. Irregular dimensions avoid a repeated square grid.
        def inlay(x,y,z,h,w,color=3):
            m.poly([(x,y,z),(x,y+h,z),(x,y+h,z+w),(x,y,z+w)],[0,0,0],color)
        if kind==0:
            for y,z,h,w in ((-250,30,95,110),(-140,165,115,125),(-15,25,90,120),
                            (85,30,75,100),(175,145,90,115),(290,25,95,250)):
                x=-316 if 20<=y<300 else -329
                inlay(x,y,z,h,w,3)
                inlay(x+.5,y,z,2,w,2)
            for y in (200,211,222,233):inlay(-315,y,175,3,55,2)
        elif kind==1:
            # Axial strips sit on the two forward octagonal facets.
            for z in (25,125,235):
                for lo,hi in ((0,45),(110,155)):
                    def px(y):return -305-abs(y-85)*.253+1
                    m.poly([(px(lo),lo,z),(px(hi),hi,z),(px(hi),hi,z+65),(px(lo),lo,z+65)],[0,0,0],3)
            for y in (-220,310):inlay(-399,y,35,50,240,3)
        elif kind==2:
            for y in (-510,-400,235,360):
                for z,w in ((30,100),(155,130)):
                    inlay(-344,y,z,70,w,3)
                    inlay(-343.5,y,z,2,w,2)
        elif kind==3:
            for y,z in ((-245,35),(-60,50),(150,120)):
                inlay(-479,y,z,45,155,3)
            for y in (-405,-345,260,330):inlay(-368 if y>0 else -384,y,40,40,235,3)
        else:
            for y,z,h,w in ((-410,30,95,230),(-75,30,100,120),(40,170,50,120)):
                inlay(-419,y,z,h,w,3)
            for y,z in ((155,70),(225,150)):
                inlay(-257,y,z,50,80,3)
            for y in (166,176,186,196):inlay(-256,y,82,3,55,2)
        assert len(m.v)<=255 and len(m.f)<=255
        result.append(m)
    return result
