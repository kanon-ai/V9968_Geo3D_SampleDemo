import os,shutil
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import cv2
P=Path(__file__).parent.resolve();M=P/'media';M.mkdir(exist_ok=True)
FF=os.environ.get('FFMPEG') or shutil.which('ffmpeg')
assert FF, 'Set FFMPEG to ffmpeg executable'
FONT=os.environ.get('CAPTION_FONT','C:/Windows/Fonts/bahnschrift.ttf')
band=Image.new('RGB',(960,60),(7,15,26));d=ImageDraw.Draw(band)
d.text((20,6),'SKYBOUND / LOW ALTITUDE   -   V9968 + Geo3D',font=ImageFont.truetype(FONT,22),fill=(225,230,239))
d.text((20,33),'TurboR | real-time polygon rendering | openMSX evaluation | automatic demo',font=ImageFont.truetype(FONT,16),fill=(153,187,210))
band.save(P/'out/caption.png')
def run(args):subprocess.run([str(FF),'-v','error','-y',*args],check=True)
mp4=M/'SKYBOUND-textured-flight-v2.mp4';gif=M/'SKYBOUND-textured-flight-v2-under15MB.gif'
run(['-i',str(P/'out/SKYBOUND-raw.avi'),'-i',str(P/'out/caption.png'),'-filter_complex','[0:v]scale=960:720:flags=neighbor,pad=960:780:0:0:black[v];[v][1:v]overlay=0:720[out]','-map','[out]','-an','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)])
for width,height in ((480,390),(432,351),(384,312)):
    run(['-i',str(mp4),'-filter_complex',f'fps=20,scale={width}:{height}:flags=neighbor,split[a][b];[a]palettegen=max_colors=32[p];[b][p]paletteuse=dither=none','-loop','0',str(gif)])
    if gif.stat().st_size<15000000:break
assert gif.stat().st_size<15000000
cap=cv2.VideoCapture(str(mp4));fps=cap.get(cv2.CAP_PROP_FPS);n=cap.get(cv2.CAP_PROP_FRAME_COUNT);ok,frame=cap.read();assert ok;cap.release()
duration=0
with Image.open(gif) as im:
    for i in range(im.n_frames):im.seek(i);im.load();duration+=im.info.get('duration',0)
assert abs(duration/1000-n/fps)<.15
run(['-i',str(mp4),'-f','null','-'])
meta={'seconds':n/fps,'gif_seconds':duration/1000,'gif_dimensions':[width,height],'silent':True,'speed_adjustment':False,'source':'dedicated Geo3D openMSX capture; physical hardware unverified','files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (mp4,gif)}}
(M/'manifest.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
