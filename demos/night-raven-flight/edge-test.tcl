set root [file dirname [file normalize [info script]]]
set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set sound_driver null
set power on
set log [open [file join $root out edge-test-log.txt] w]
proc rd {a} {debug read memory $a}
proc ck {condition message} {global log;if {!$condition} {puts $log "FAIL $message";close $log;exit};puts $log "PASS $message";flush $log}
proc tick {} {expr {[rd 0xE506]+256*[rd 0xE507]}}
after time 7 {keymatrixdown 8 1}
after time 7.3 {keymatrixup 8 1;keymatrixdown 8 48}
after time 10 {ck [expr {[rd 0xE501]==42 && [rd 0xE502]==92}] bounds_top_left;keymatrixup 8 255;keymatrixdown 8 192}
after time 15.0 {ck [expr {[rd 0xE501]==214 && [rd 0xE502]==175}] bounds_bottom_right;keymatrixup 8 255;keymatrixdown 7 4}
after time 15.3 {keymatrixup 7 4;set frozen [tick];ck [expr {[rd 0xE513]==1}] pause_on}
after time 17.0 {ck [expr {[tick]==$frozen}] pause_freezes_simulation;keymatrixdown 7 4}
after time 17.3 {keymatrixup 7 4}
after time 18.0 {ck [expr {[tick]>$frozen}] resume;keymatrixdown 6 32}
after time 18.3 {keymatrixup 6 32}
after time 19.0 {ck [expr {[rd 0xE503]==8 && [tick]<30}] restart;watch_death}
proc watch_death {} {
 global log root
 if {[rd 0xE500]==2} {puts $log "PASS no_input_can_lose tick=[tick]";keymatrixdown 8 1;after time 0.3 {keymatrixup 8 1;ck [expr {[rd 0xE500]==1 && [rd 0xE503]==8}] retry_after_death;puts $log END;close $log;exit};return}
 after time 0.1 watch_death
}
after time 100 {puts $log TIMEOUT;close $log;exit}
after realtime 100 {puts $log TIMEOUT;close $log;exit}
