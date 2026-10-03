"""SCREEN 8 / EPAL assets. VRAM regions exclude both visible framebuffers."""
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
BANKS=[4,5,6,7,52,53,54,56,57,58]
BLOCKS=[3,7,8,9,10,11,12,13,14,15]
HUD_ROWS=[226,240,468,482,496]

def make(base,flat,hud):
    src=Image.open(ROOT/'assets/material-atlas-v1.png').convert('RGB');w,h=src.size
    sky=src.crop((0,0,w//2,h//2)).resize((256,96),Image.Resampling.LANCZOS)
    office=src.crop((w//2,0,w,h//2)).resize((128,128),Image.Resampling.LANCZOS)
    shop=src.crop((w//2,h//2,w,h)).resize((64,64),Image.Resampling.LANCZOS)
    sample=Image.new('RGB',(256,256));sample.paste(sky,(0,0));sample.paste(office,(0,96));sample.paste(shop,(128,96))
    adaptive=sample.quantize(colors=224,method=Image.Quantize.MEDIANCUT).getpalette()[:224*3]
    extra=[tuple(adaptive[i:i+3]) for i in range(0,len(adaptive),3)]
    # BASE bit7 is the Geo3D texture flag: duplicate the low flat colors so
    # toggling CTRL textures off still produces the same flat material colors.
    colors=base+extra[:112]+base+extra[112:]
    assert len(colors)==256
    palette=Image.new('P',(1,1));palette.putpalette(sum(map(list,colors),[]))
    def quant(im):return im.quantize(palette=palette,dither=Image.Dither.NONE)
    textured=Image.new('P',(256,184),2);textured.putpalette(palette.getpalette())
    textured.paste(quant(sky.crop((0,24,256,96))),(0,0))
    atlas=Image.new('P',(256,128),2);atlas.putpalette(palette.getpalette())
    atlas.paste(quant(office),(0,0));atlas.paste(quant(shop),(192,0))
    vram=np.zeros((1024,256),dtype=np.uint8)
    vram[512:696]=np.asarray(flat)[24:208]
    vram[696:880]=np.asarray(textured)
    vram[880:1008]=np.asarray(atlas)
    vram[212:226]=np.asarray(hud)[:14]
    for i,y in enumerate(HUD_ROWS):vram[y:y+14]=np.asarray(hud)[16+i*16:30+i*16]
    vram[1008:1022]=np.asarray(hud)[240:254]
    raw=vram.tobytes()
    return colors,{bank:bytearray(raw[block*16384:(block+1)*16384]) for bank,block in zip(BANKS,BLOCKS)},textured,atlas
