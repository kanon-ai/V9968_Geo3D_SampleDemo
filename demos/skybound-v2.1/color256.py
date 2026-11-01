from PIL import Image,ImageDraw
from hudfont import label
import numpy as np

def make(base,hud,root,out):
    atlas=Image.new('RGB',(256,256),(32,32,32))
    material=Image.open(root/'assets/japan-materials-generated.png').convert('RGB')
    w,h=material.size
    for i in range(8):
        x=i%4;y=i//4
        tile=material.crop((x*w//4,y*h//2,(x+1)*w//4,(y+1)*h//2)).resize((64,64),Image.Resampling.LANCZOS)
        atlas.paste(tile,(x*64,y*64))
    instruments=Image.open(root/'assets/cockpit-instruments-generated.png').convert('RGB');w,h=instruments.size
    for i in range(4):
        tile=instruments.crop((i*w//4,int(h*.08),(i+1)*w//4,int(h*.88))).resize((64,64),Image.Resampling.LANCZOS)
        atlas.paste(tile,(i*64,128))
    ground=Image.open(root/'assets/ground-generated.png').convert('RGB');w,h=ground.size
    for i in range(4):
        atlas.paste(ground.crop((i*w//4,0,(i+1)*w//4,h)).resize((64,64),Image.Resampling.LANCZOS),(i*64,192))
    atlas.paste(atlas.crop((128,64,192,128)),(0,0)) # relocate castle stone
    atlas.paste(atlas.crop((192,64,256,128)),(192,192)) # relocate water
    atlas.paste(Image.open(root/'assets/fuji-generated.png').convert('RGB').resize((256,64),Image.Resampling.LANCZOS),(0,64))
    sky=Image.open(root/'assets/sky-generated.png').convert('RGB').resize((256,256),Image.Resampling.LANCZOS)
    samples=Image.new('RGB',(256,512));samples.paste(atlas);samples.paste(sky,(0,256))
    q=samples.quantize(colors=224,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    raw=q.getpalette();extra=[tuple(raw[i:i+3]) for i in range(0,224*3,3)]
    colors=list(base)+extra[:112]+list(base)+extra[112:]
    palette=Image.new('P',(1,1));palette.putpalette([v for c in colors for v in c])
    def quant(im):return im.quantize(palette=palette,dither=Image.Dither.NONE)
    sky=quant(sky);atlas=quant(atlas)
    sky.save(out/'sky256.png');atlas.save(out/'atlas256.png')
    vram=bytearray(262144)
    vram[512*256:768*256]=sky.tobytes();vram[768*256:]=atlas.tobytes()
    a=np.array(hud)
    for i,dest in enumerate([212,226,240,468,482,496]):
        strip=a[i*16:i*16+14,:].astype('uint8').tobytes()
        vram[dest*256:dest*256+len(strip)]=strip
    for yy,text in [(226,'HOKKAIDO / TOHOKU'),(240,'TOKYO / TOWERS'),(468,'MT FUJI / SNOW PEAK'),(482,'NAGOYA / KYOTO'),(496,'OSAKA / SETO INLAND SEA'),(704,'KYUSHU / VOLCANOES'),(718,'OKINAWA / BLUE ISLANDS'),(732,'HOKKAIDO / TAKEOFF'),(746,'OKINAWA / LANDING')]:
        strip=Image.new('P',(256,14));label(ImageDraw.Draw(strip),(5,0),text,fill=5);vram[yy*256:(yy+14)*256]=strip.tobytes()
    resources={}
    for bank,block in [(4,8),(5,9),(6,10),(7,11),(108,12),(109,13),(110,14),(111,15),(112,3),(113,7)]:resources[bank]=vram[block*16384:(block+1)*16384]
    return colors,resources
