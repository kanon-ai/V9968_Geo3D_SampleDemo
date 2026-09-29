set root [file dirname [file normalize [info script]]]
set auto_save_settings false
set renderer SDLGL-PP
set throttle off
set speed 100
set sound_driver null
set power on
set pause off
set started 0
set targets {100 180 295 340 385 600 780 850 900 1160 1325 1350 1450}
set log [open [file join $root out capture-log.txt] w]
proc observe {} {
 global started startframe targets log root
 set n [expr {[debug read memory 0xE420]+256*[debug read memory 0xE421]}]
 if {!$started && $n>=32 && $n<500} {
  record start [file normalize $root/out/ORBITAL-raw.avi]
  puts $log "START frame=$n time=[machine_info time]"
  set started 1
  set startframe $n
 }
 if {$started && [llength $targets] && $n>=[lindex $targets 0]} {
  screenshot -raw [format "$root/out/frame-%04d.png" [lindex $targets 0]]
  puts $log "FRAME frame=$n time=[machine_info time]"
  flush $log
  set targets [lrange $targets 1 end]
 }
 if {$started && $n>=$startframe+1536} {
  record stop
  puts $log "END frame=$n time=[machine_info time]"
  close $log
  exit
 }
 after time 0.01 observe
}
after time 6 observe
after time 120 {catch {record stop};puts $log "TIMEOUT";close $log;exit}
after realtime 55 {catch {record stop};puts $log "WALL_TIMEOUT";close $log;exit}
