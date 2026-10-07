from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parent
runtime=Path(os.environ['GEO3D_RUNTIME']).resolve()
env=os.environ.copy()
# Set system data; inherit the user's own BIOS and preferences location.
env['OPENMSX_SYSTEM_DATA']=str(runtime/'share')
subprocess.run([str(runtime/'openmsx.exe'),'-machine','Panasonic_FS-A1ST_V9968','-ext','geo3d','-cart',str(root/'out'/'NIGHT_RAVEN_THREE_STAGE.ROM'),'-romtype','ASCII16','-script',str(root/'boss-motion.tcl')],env=env,cwd=runtime,timeout=240,check=True)
