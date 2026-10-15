from pathlib import Path
import subprocess,os,json,hashlib
P=Path(__file__).resolve().parent
oldrom=Path(os.environ['NR_BASELINE_ROM']).resolve()
results={}
for case,rt,rom in [('old','old',oldrom),('compat','v2',oldrom),('resident','v2',P/'out/NIGHT_RAVEN_GEO3D_V2.ROM')]:
 R=Path(os.environ['GEO3D_OLD_RUNTIME' if rt=='old' else 'GEO3D_V2_RUNTIME']).resolve();O=P/'out/comparison'/case;O.mkdir(parents=True,exist_ok=True)
 script=r"""set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set speed 100
set sound_driver null
set power on
set scene 0
set f [open {OUT/timing.csv} w]
puts $f "scene,frames,seconds"
proc nr_v2_bench_donecount {} {expr {[debug read memory 0xE420]+256*[debug read memory 0xE421]}}
proc nr_v2_bench_setup {} {
 global scene
 incr scene
 if {$scene>5} {close $::f;exit}
 foreach {a v} {0xE500 1 0xE513 1 0xE501 128 0xE502 145 0xE503 8 0xE506 128 0xE507 0 0xE202 128 0xE203 1 0xE512 0 0xE600 1 0xE601 90 0xE602 70 0xE603 100 0xE604 64 0xE605 1 0xE610 1 0xE611 170 0xE612 80 0xE613 130 0xE614 64 0xE615 2 0xE620 1 0xE621 125 0xE622 60 0xE623 60 0xE624 64 0xE625 3 0xE630 0} {debug write memory $a $v}
 debug write memory 0xE534 [expr {$scene==1?1:2}]
 if {$scene==3} {debug write memory 0xE506 144;debug write memory 0xE507 1}
 if {$scene==4} {debug write memory 0xE534 3;debug write memory 0xE512 1;debug write memory 0xE605 6;debug write memory 0xE610 0;debug write memory 0xE620 0}
 if {$scene==5} {debug write memory 0xE534 3;debug write memory 0xE512 1}
 after time 1 nr_v2_bench_begin
}
proc nr_v2_bench_begin {} {set ::start [nr_v2_bench_donecount];set ::at [machine_info time];after time .001 nr_v2_bench_poll}
proc nr_v2_bench_poll {} {
 set n [nr_v2_bench_donecount]
 if {$n-$::start>=600} {
 puts $::f "$::scene,[expr {($n-$::start)/3}],[expr {[machine_info time]-$::at}]";flush $::f
 set page [expr {([debug read "VDP regs" 2]>>5)&1}]
 set out [open "OUT/scene-$::scene.bin" wb];fconfigure $out -translation binary
 puts -nonewline $out [debug read_block VRAM [expr {$page*32768}] 27136];close $out
 after realtime .2 {screenshot -raw "OUT/scene-$::scene.png";nr_v2_bench_setup}
 } else {after time .001 nr_v2_bench_poll}
}
after time 12 nr_v2_bench_setup
after realtime 100 {exit}
""".replace('OUT',O.as_posix())
 scriptpath=O/'bench.tcl';scriptpath.write_text(script)
 env=os.environ.copy();env.update(OPENMSX_SYSTEM_DATA=str(R/'share'),OPENMSX_USER_DATA=str(R/'userdata'),OPENMSX_HOME=str(R/'home'))
 run=subprocess.run([str(R/'openmsx.exe'),'-machine','Panasonic_FS-A1ST_V9968','-ext','geo3d','-cart',str(rom),'-romtype','ASCII16','-script',str(scriptpath)],env=env,cwd=R,check=False,timeout=110)
 assert run.returncode==0, f"Unexpected emulator exit: {run.returncode}"
 import csv
 rows=list(csv.DictReader((O/'timing.csv').open()));assert len(rows)==5
 print('emulator exit',case,run.returncode,flush=True)
 results[case]={x['scene']:float(x['frames'])/float(x['seconds']) for x in rows};print(case,results[case],flush=True)
results['pixels']={str(i):{'compat':(P/f'out/comparison/old/scene-{i}.bin').read_bytes()==(P/f'out/comparison/compat/scene-{i}.bin').read_bytes(),'resident':(P/f'out/comparison/old/scene-{i}.bin').read_bytes()==(P/f'out/comparison/resident/scene-{i}.bin').read_bytes()} for i in range(1,6)}
(P/'out/comparison/results.json').write_text(json.dumps(results,indent=2));print(results)
