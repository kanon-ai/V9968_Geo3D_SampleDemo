set root [file dirname [file normalize [info script]]]
set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set sound_driver null
set power on
set log [open [file join $root out playtest-log.txt] w]
proc rd {a} {debug read memory $a}
set stamp [clock milliseconds]
set n 0
set done 0
proc bot {} {
 global root log n done stamp
 incr n
 set frame [expr {[rd 0xE202]+256*[rd 0xE203]}]
 if {$frame<12 || $frame>1523} {screenshot -raw [file join $root out seam-$stamp-$n-$frame.png]}
 set state [rd 0xE500]
 set tick [expr {[rd 0xE506]+256*[rd 0xE507]}]
 if {$state==0} {keymatrixdown 8 1}
 if {$state==4} {keymatrixup 8 255;keymatrixup 5 32}
 if {$state==1} {
  set px [rd 0xE501];set py [rd 0xE502]
  set best 99999;set tx 128;set ty 140;set aimhp 0
  for {set j 0} {$j<4} {incr j} {
   set a [expr {0xE600+16*$j}]
   if {![rd $a]} continue
   set x [rd [expr {$a+1}]];set y [expr {[rd [expr {$a+2}]]+55}];if {$y>173} {set y 173}
   set dx [expr {$x-$px}];if {$dx<0} {set dx [expr {-$dx}]};set dy [expr {$y-$py}];if {$dy<0} {set dy [expr {-$dy}]};set dist [expr {$dx+$dy}]
   if {$j==0 && [rd 0xE512]} {set dist -1}
   if {$dist<$best} {set best $dist;set tx $x;set ty $y;set aimhp [rd [expr {$a+4}]]}
  }
  set mask 1
  if {$tx>$px+5} {set mask [expr {$mask|128}]}
  if {$tx<$px-5} {set mask [expr {$mask|16}]}
  if {$ty>$py+5} {set mask [expr {$mask|64}]}
  if {$ty<$py-5} {set mask [expr {$mask|32}]}
  keymatrixup 8 255;keymatrixdown 8 $mask
  if {$aimhp>=3} {keymatrixdown 5 32} else {keymatrixup 5 32}
 }
 if {[rd 0xE511]>=10 && $n%3==0} {screenshot -raw [file join $root out lock-$stamp-$n.png]}
 if {$n%100==0 || $state==2 || $state==3} {
  puts $log "time=[machine_info time] stage=[rd 0xE534] state=$state tick=$tick kills=[rd 0xE505] pause=[rd 0xE513] shield=[rd 0xE503] missiles=[rd 0xE504] boss=[rd 0xE512]"
  flush $log
 }
 if {[rd 0xE515]>0 && $n%4==0 && $n<200} {screenshot -raw [file join $root out blast-$stamp-$n.png]}
 if {$state==5 && $n%12==0} {screenshot -raw [file join $root out boss-blast-$stamp-$n.png]}
 if {$n%80==0} {screenshot -raw [file join $root out bot-$stamp-$n.png]}
 if {$state==2 || $state==3} {keymatrixup 8 255;keymatrixup 5 32;after time 0.3 {screenshot -raw [file join $root out result-$stamp.png];record stop;puts $log END;close $log;exit};return}
 after time 0.05 safe_bot
}
after time 10 {record start [file join $root out gameplay-$stamp.avi];screenshot -raw [file join $root out game-title-$stamp.png];after time 2 safe_bot}
after time 210 {puts $log TIMEOUT;close $log;exit}
after realtime 210 {puts $log TIMEOUT;close $log;exit}

proc safe_bot {} {if {[catch {bot} err]} {global log;puts $log "ERROR $err";flush $log;exit}}
