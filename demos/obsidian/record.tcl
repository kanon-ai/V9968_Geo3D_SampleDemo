set root [file dirname [file normalize [info script]]]
set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set speed 100
set sound_driver null
set power on
set pause off
set started 0
set log [open [file join $root out record-log.txt] w]
proc poll_record {} {
 global started log root
 set n [expr {[debug read memory 0xE420]+256*[debug read memory 0xE421]}]
 if {!$started && $n >= 16 && $n < 100} {
  record start [file join $root out OBSIDIAN-raw.avi]
  puts $log "start_frame=$n start_time=[machine_info time]"
  flush $log
  set started 1
 }
 if {$started && $n >= 528} {
  screenshot -raw [file join $root out final-frame.png]
  record stop
  puts $log "end_frame=$n end_time=[machine_info time]"
  close $log
  exit
 }
 after time 0.01 poll_record
}
after time 5.5 poll_record
after realtime 55 {catch {record stop};close $log;exit}
