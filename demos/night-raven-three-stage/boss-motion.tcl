set root [file dirname [file normalize [info script]]]
set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set sound_driver null
set power on
set log [open [file join $root out boss-motion-r27.txt] w]
proc count {} {expr {[debug read memory 0xE420]+256*[debug read memory 0xE421]}}
set n 0
proc sample {} {
 global n root
 foreach {a v} {0xE500 1 0xE513 0 0xE534 2 0xE512 1 0xE600 1 0xE604 64 0xE605 2 0xE50C 255 0xE501 214 0xE502 140 0xE503 8 0xE202 0 0xE203 1 0xE507 0 0xE610 0 0xE620 0 0xE630 0} {debug write memory $a $v}
 debug write memory 0xE506 64
 debug write memory 0xE507 1
 after time 0.2 {after realtime 0.15 capture}
}
proc capture {} {
 global n root log
 puts $log "[machine_info time] tick=[debug read memory 0xE506] x=[debug read memory 0xE601] y=[debug read memory 0xE602] depth=[debug read memory 0xE603]"
 flush $log
 debug write memory 0xE503 8
 debug write memory 0xE50C 255
 incr n
 if {$n<32} {after time 0.5 capture} else {close $log;exit}
}
after time 12 sample
after realtime 60 {exit}
