import os
"""Encode real emulator recording at its original emulated-time playback rate."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FF=Path(os.environ['FFMPEG']).resolve()
MEDIA=ROOT/'media';MEDIA.mkdir(exist_ok=True)
band=Image.new('RGB',(960,60),(5,9,17));d=ImageDraw.Draw(band)
font=ImageFont.truetype(os.environ['CAPTION_FONT'],20)
d.text((24,7),'GEO3D EXPERIMENT  /  openMSX evaluation capture',font=font,fill=(160,210,224))
d.text((24,32),'1,816 vertices / 1,302 faces submitted per frame | NO SPEED-UP',font=ImageFont.truetype(os.environ['CAPTION_FONT'],16),fill=(144,159,178))
band.save(ROOT/'out/caption.png')
mp4=MEDIA/'OBSIDIAN-v0.2.0-silent.mp4'
subprocess.run([str(FF),'-y','-i',str(ROOT/'out/OBSIDIAN-raw.avi'),'-i',str(ROOT/'out/caption.png'),'-filter_complex','[0:v]fps=30,scale=960:720:flags=neighbor,pad=960:780:0:0:black[v];[v][1:v]overlay=0:720[out]','-map','[out]','-an','-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
gif=MEDIA/'OBSIDIAN-v0.2.0-preview.gif'
subprocess.run([str(FF),'-y','-ss','4','-t','16','-i',str(mp4),'-filter_complex','fps=15,scale=480:390:flags=neighbor,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=none','-loop','0',str(gif)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
subprocess.run([str(FF),'-v','error','-i',str(mp4),'-f','null','-'],check=True)
assert gif.stat().st_size<15_000_000
with Image.open(gif) as im:
    durations=[]
    for n in range(im.n_frames):im.seek(n);durations.append(im.info.get('duration',0))
    assert 15900<=sum(durations)<=16100
metadata={'source':'actual openMSX geo3d AVI','speed_adjustment':False,'mp4_full_loop_seconds_approximately':34.18,'gif_excerpt_seconds':sum(durations)/1000,'gif_frames':len(durations),'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (mp4,gif)}}
(MEDIA/'media-manifest.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata,indent=2))
