import os
"""Encode actual emulator frames at their recorded playback speed."""
from pathlib import Path
import subprocess, json, hashlib, re
from PIL import Image, ImageDraw, ImageFont
import cv2
ROOT = Path(__file__).resolve().parent
FF = Path(os.environ['FFMPEG']).resolve()
MEDIA = ROOT/'media'
MEDIA.mkdir(exist_ok=True)
band = Image.new('RGB', (960,60), (5,9,17))
d = ImageDraw.Draw(band)
d.text((24,7), 'NIGHT RAVEN / HULL BREACH / V9968 + Geo3D', font=ImageFont.truetype(os.environ['CAPTION_FONT'],20), fill=(160,210,224))
d.text((24,33), 'V9968 background / effects + Geo3D geometry | openMSX evaluation', font=ImageFont.truetype(os.environ['CAPTION_FONT'],16), fill=(144,159,178))
band.save(ROOT/'out/caption.png')
def run(args):
    subprocess.run([str(FF),'-y',*args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
mp4 = MEDIA/'NIGHT-RAVEN-v0.2.0-silent.mp4'
run(['-i',str(ROOT/'out/NIGHT-RAVEN-raw.avi'),'-i',str(ROOT/'out/caption.png'),'-filter_complex','[0:v]scale=960:720:flags=neighbor,pad=960:780:0:0:black[v];[v][1:v]overlay=0:720[out]','-map','[out]','-an','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)])
gif = MEDIA/'NIGHT-RAVEN-v0.2.0-silent.gif'
run(['-i',str(mp4),'-filter_complex','fps=20,scale=432:351:flags=neighbor,split[a][b];[a]palettegen=max_colors=32:stats_mode=diff[p];[b][p]paletteuse=dither=none','-loop','0',str(gif)])
run(['-v','error','-i',str(mp4),'-f','null','-'])
cap = cv2.VideoCapture(str(mp4))
fps = cap.get(cv2.CAP_PROP_FPS)
frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
ok, frame = cap.read()
assert ok and frame.shape[:2] == (780,960)
cap.release()
assert 15 < frames/fps < 100 and 59 < fps < 61
assert gif.stat().st_size < 15_000_000
with Image.open(gif) as im:
    durations = []
    for i in range(im.n_frames):
        im.seek(i)
        durations.append(im.info.get('duration',0))
    assert abs(sum(durations)/1000-frames/fps)<0.15
log = (ROOT/'out/capture-log.txt').read_text()
samples = re.findall(r'(?:START|END) frame=(\d+) time=([\d.]+)', log)
updates = (int(samples[1][0])-int(samples[0][0]))/(float(samples[1][1])-float(samples[0][1]))
meta = {'source':'actual openMSX geo3d capture','speed_adjustment':False,'mp4_frames':frames,'mp4_fps':fps,'mp4_seconds':frames/fps,'simulation_ticks_per_second':updates,'render_updates_per_second':updates/3,'hardware_performance_verified':False,'audio':'none; silent ROM and video','gif_frames':len(durations),'gif_seconds':sum(durations)/1000,'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (mp4,gif)}}
(MEDIA/'media-manifest.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
