from pathlib import Path
import os,subprocess,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
ff=os.environ['FFMPEG']
media=ROOT/'media';media.mkdir(exist_ok=True)
avi=max((ROOT/'out').glob('gameplay-*.avi'),key=lambda p:p.stat().st_mtime)
mp4=media/'NIGHT-RAVEN-Flight-Development-Demo-v0.4.0.mp4'
gif=media/'night-raven-flight.gif'
def run(args):return subprocess.run([ff,'-v','error','-y']+args,check=True,capture_output=True)
pcm=run(['-i',str(avi),'-map','0:a:0','-f','s16le','-']).stdout
a=np.frombuffer(pcm,dtype='<i2').astype(np.int32)
assert len(a)>10000 and np.max(np.abs(a))>0
run(['-i',str(avi),'-vf','scale=640:480:flags=neighbor','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(mp4)])
run(['-ss','5','-t','12','-i',str(mp4),'-filter_complex','fps=15,scale=432:324:flags=neighbor,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=none','-loop','0',str(gif)])
assert gif.stat().st_size<15000000
run(['-i',str(mp4),'-f','null','-'])
assert run(['-i',str(mp4),'-map','0:a:0','-f','s16le','-']).stdout
report={'audio':'temporary PSG effects, no BGM','capture':'keyboard-only automatic test in developer openMSX','pcm_samples':len(a),'pcm_peak':int(np.max(np.abs(a))),'pcm_rms':float(np.sqrt(np.mean(a.astype(float)**2))),'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [mp4,gif]}}
(media/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
