"""Pack original AI-generated material tiles for V9968 LRMM faces."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def images(colors):
    src=Image.open(ROOT/'assets/material-atlas-v1.png').convert('RGB')
    w,h=src.size
    tiles=[src.crop(box) for box in ((0,0,w//2,h//2),(w//2,0,w,h//2),(0,h//2,w//2,h),(w//2,h//2,w,h))]
    palette=Image.new('P',(1,1));palette.putpalette(sum(map(list,colors),[])+[0]*720)
    def quant(im):return im.quantize(palette=palette,dither=Image.Dither.NONE)
    sky=Image.new('P',(256,256),2);sky.putpalette(palette.getpalette())
    sky.paste(quant(tiles[0].resize((256,96),Image.Resampling.LANCZOS)),(0,0))
    atlas=Image.new('RGB',(256,128))
    atlas.paste(tiles[1].resize((128,128),Image.Resampling.LANCZOS),(0,0))
    armor=quant(tiles[2].resize((64,128),Image.Resampling.LANCZOS))
    atlas.paste(armor.convert('RGB'),(128,0))
    atlas.paste(tiles[3].resize((64,64),Image.Resampling.LANCZOS),(192,0))
    # The rival shares the armor's seams/detail, but has blue paint.
    a=np.array(armor.resize((64,64),Image.Resampling.NEAREST))
    lut=np.arange(256,dtype=np.uint8);lut[[4,5,6,13,14,15]]=[12,13,11,13,12,12]
    blue=Image.fromarray(lut[a]);blue.putpalette(palette.getpalette())
    atlas.paste(blue.convert('RGB'),(192,64))
    return sky,quant(atlas)

def mapped(mesh,kind=None,blue=False):
    uv=bytearray();faces=[]
    for ids,n,c in mesh.f:
        p=np.array([mesh.v[i] for i in ids],float);span=np.ptp(p,axis=0)
        enabled=False;rect=(0,0,127,127)
        if kind is not None:
            # Vertical architecture only: roads, roofs and plaza stay flat.
            # Map the inset panes; keep the structural mass cheap and readable.
            from city import MAP
            h=MAP['districts'][kind]['height']
            enabled=kind!='plaza' and 30<span[1]<h*.65 and min(span[0],span[2])<2
            if kind=='retail':rect=(192,0,255,63)
        # Armor occupies only a handful of output pixels per face. Preserve
        # its original flat facet colors instead of minifying seam texels.
        axes=np.argsort(span)[-2:]
        # Vertical direction in source images points down.
        va=1 if span[1]>1 and 1 in axes else int(axes[0]);ua=next(int(k) for k in axes if k!=va)
        u=(p[:,ua]-p[:,ua].min())/max(span[ua],1)
        v=1-(p[:,va]-p[:,va].min())/max(span[va],1)
        x0,y0,x1,y1=rect
        uv.extend(bytes(np.column_stack((x0+u*(x1-x0),y0+v*(y1-y0))).round().astype('uint8').flat))
        col=({4:11,5:12,6:13}.get(c,c) if blue else c)
        faces.append((ids,n,col|(128 if enabled else 0)))
    mesh.f=faces
    return mesh,uv
