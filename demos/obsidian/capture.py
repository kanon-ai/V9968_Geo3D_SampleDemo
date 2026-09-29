from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parent
runtime=Path(os.environ['GEO3D_RUNTIME']).resolve()
env=os.environ.copy()
# Set system data; inherit the user's own BIOS and preferences location.
env['OPENMSX_SYSTEM_DATA']=str(runtime/'share')
subprocess.run([str(runtime/'openmsx.exe'),'-machine','Panasonic_FS-A1ST_V9968','-ext','geo3d','-cart',str(root/'out/OBSIDIAN_GEO3D.ROM'),'-romtype','ASCII16','-script',str(root/'record.tcl')],env=env,cwd=runtime,timeout=65,check=True)
log=(root/'out/record-log.txt').read_text();print(log)
assert 'end_frame=' in log and 'TIMEOUT' not in log
