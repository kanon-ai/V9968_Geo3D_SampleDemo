MOFFSET=0xE53E
BDEATH=0xE538
BCX=0xE539
BCY=0xE53A
MTRAIL=0xE6C0
STAGE=0xE534
TRANSITION=0xE535
RIVALMAT=0xE740
; NIGHT RAVEN interactive game. All combat state lives in RAM.
GS=0xE500
PX=0xE501
PY=0xE502
SH=0xE503
AMMO=0xE504
KILLS=0xE505
TICK=0xE506
FIRE=0xE508
MISS=0xE509
PREV=0xE50A
DIR=0xE50B
INV=0xE50C
COOL=0xE50D
RELOAD=0xE50E
SPAWN=0xE50F
LOCK=0xE510
LOCKN=0xE511
BOSS=0xE512
PAUSED=0xE513
RNG=0xE514
FLASH=0xE515
FX=0xE516
FY=0xE517
MLIFE=0xE518
MX=0xE519
MY=0xE51A
MTARGET=0xE51B
CUR=0xE51C
TX=0xE51D
TY=0xE51E
LASTLOCK=0xE524
COL=0xE51F
LX=0xE520
LY=0xE521
RX=0xE522
RY=0xE523
EBASE=0xE600
BBASE=0xE640
; Enemy: active, x, y, age, hp, kind, turn, shoot countdown.
; Shot: active, x, y, dx, dy (8 bytes per slot).
game_init:
 xor a
 ld (SOUND),a
 ld (SOUND_KIND),a
 ld a,#8
 out (0xA0),a
 xor a
 out (0xA1),a
 ld hl,#GS
 ld de,#GS+1
 ld bc,#0x1BF
 ld (hl),#0
 ldir
 ld a,#1
 ld (STAGE),a
 ld a,#128
 ld (PX),a
 ld a,#154
 ld (PY),a
 ld a,#8
 ld (SH),a
 ld a,#3
 ld (AMMO),a
 ld a,#8
 ld (BANKANGLE),a
 ld a,#4
 ld (PITCHANGLE),a
 ld a,#93
 ld (RNG),a
 ld a,#255
 ld (LOCK),a
 ret
new_game:
 ld a,(GS)
 cp #2
 ld a,#1
 jr nz,ng_stage
 ld a,(STAGE)
ng_stage:
 push af
 call game_init
 pop af
 ld (STAGE),a
 ld a,#1
 ld (GS),a
 ld (PREV),a
 ret
read_input:
 xor a
 call 0x00D5
 ld (DIR),a
 or a
 jr nz,ri_trigger
 ld a,#1
 call 0x00D5
 ld (DIR),a
ri_trigger:
 xor a
 call 0x00D8
 ld (FIRE),a
 ld a,#1
 call 0x00D8
 ld b,a
 ld a,(FIRE)
 or b
 ld (FIRE),a
 ld a,#5
 call 0x0141
 cpl
 and #32
 ld (MISS),a
 ld a,#3
 call 0x00D8
 ld b,a
 ld a,(MISS)
 or b
 ld (MISS),a
 ret
game_tick:
 ld a,(GS)
 cp #5
 jp z,boss_death_tick
 ld a,(GS)
 cp #4
 jr nz,stage_input
 ld hl,#TRANSITION
 dec (hl)
 ret nz
 ld a,(STAGE)
 push af
 call game_init
 pop af
 ld (STAGE),a
 ld a,#1
 ld (GS),a
 ret
stage_input:
 call read_input
 ld a,#6
 call 0x0141
 bit 5,a
 jr nz,gt_no_restart
 jp new_game
gt_no_restart:
 ld a,#7
 call 0x0141
 cpl
 and #4
 ld b,a
 ld a,(PREV)
 and #4
 xor b
 and b
 jr z,gt_pause_done
 ld a,(PAUSED)
 xor #1
 ld (PAUSED),a
gt_pause_done:
 ld a,(FIRE)
 and #1
 or b
 ld c,a
 ld a,(PREV)
 ld (PREV),a
 ld a,(GS)
 cp #1
 jr z,gt_play
 ld a,(PREV)
 and #1
 ld b,a
 ld a,c
 ld (PREV),a
 and #1
 ret z
 ld a,b
 or a
 ret nz
 jp new_game
gt_play:
 ld a,c
 ld (PREV),a
 ld a,(PAUSED)
 or a
 ret nz
 call visual_tick
 ld hl,(TICK)
 inc hl
 ld (TICK),hl
 ld a,(INV)
 or a
 jr z,gt_cool
 dec a
 ld (INV),a
gt_cool:
 ld a,(COOL)
 or a
 jr z,gt_flash
 dec a
 ld (COOL),a
gt_flash:
 ld a,(FLASH)
 or a
 jr z,gt_reload
 dec a
 ld (FLASH),a
gt_reload:
 ld hl,#RELOAD
 inc (hl)
 ld a,(hl)
 cp #100
 jr c,gt_move
 ld (hl),#0
 ld a,(AMMO)
 cp #3
 jr nc,gt_move
 inc a
 ld (AMMO),a
gt_move:
 ld a,(DIR)
 or a
 jr z,gt_spawn
 dec a
 add a,a
 ld e,a
 ld d,#0
 ld hl,#directions
 add hl,de
 ld a,(PX)
 add a,(hl)
 cp #42
 jr nc,gt_xmax
 ld a,#42
gt_xmax:
 cp #215
 jr c,gt_xok
 ld a,#214
gt_xok:
 ld (PX),a
 inc hl
 ld a,(PY)
 add a,(hl)
 cp #92
 jr nc,gt_ymax
 ld a,#92
gt_ymax:
 cp #176
 jr c,gt_yok
 ld a,#175
gt_yok:
 ld (PY),a
gt_spawn:
 ld a,(STAGE)
 cp #3
 jr z,spawn_boss
 ld hl,(TICK)
 ld de,#450
 ld a,(STAGE)
 cp #2
 jr nz,boss_time_ready
 ld de,#320
boss_time_ready:
 or a
 sbc hl,de
 jr c,gt_regular
spawn_boss:
 ld a,(BOSS)
 or a
 jr nz,gt_regular
 ld a,#1
 ld (BOSS),a
 ld ix,#EBASE
 ld 0(ix),#1
 ld 1(ix),#128
 ld 2(ix),#58
 ld 3(ix),#150
 ld 4(ix),#72
 ld 5(ix),#3
 ld a,(STAGE)
 cp #1
 jr z,boss_setup_end
 ld 4(ix),#64
 ld 5(ix),#5
 cp #2
 jr z,boss_setup_end
 ld 4(ix),#160
 ld 5(ix),#6
boss_setup_end:
 ld 6(ix),#0
 ld 7(ix),#16
gt_regular:
 ld a,(STAGE)
 cp #3
 jp z,gt_enemies
 cp #2
 jr nz,stage_regular
 ld hl,(TICK)
 ld de,#12
 or a
 sbc hl,de
 jp c,gt_enemies
stage_regular:
 ld hl,#SPAWN
 inc (hl)
 ld a,(STAGE)
 cp #2
 ld a,(hl)
 jr nz,spawn_normal_interval
 cp #14
 jr spawn_interval_ready
spawn_normal_interval:
 cp #16
spawn_interval_ready:
 jr c,gt_enemies
 ld (hl),#0
 ld ix,#EBASE
 ld b,#4
gt_find:
 ld a,0(ix)
 or a
 jr z,gt_create
 ld de,#16
 add ix,de
 djnz gt_find
 jr gt_enemies
gt_create:
 call random
 and #127
 add a,#64
 ld 1(ix),a
 call random
 and #31
 add a,#42
 ld 2(ix),a
 ld 0(ix),#1
 ld 3(ix),#20
 call random
 and #3
 jr nz,gt_kind
 inc a
gt_kind:
 ld 5(ix),a
 inc a
 ld 4(ix),a
 ld 7(ix),#19
 call random
 and #1
 ld 6(ix),a
gt_enemies:
 ld ix,#EBASE
 xor a
 ld (CUR),a
ge_loop:
 ld a,0(ix)
 or a
 jp z,ge_next
 ld a,(BOSS)
 or a
 jr z,ge_normal
 ld a,(CUR)
 or a
 jr nz,ge_normal
 call boss_motion
 jr ge_shoot
ge_normal:
 inc 3(ix)
 inc 3(ix)
 ld a,3(ix)
 and #1
 jr nz,ge_drift
 inc 2(ix)
ge_drift:
 ld a,6(ix)
 or a
 jr z,ge_left
 inc 1(ix)
 ld a,1(ix)
 cp #219
 jr c,ge_age
 ld 6(ix),#0
 jr ge_age
ge_left:
 dec 1(ix)
 ld a,1(ix)
 cp #38
 jr nc,ge_age
 ld 6(ix),#1
ge_age:
 ld a,3(ix)
 cp #218
 jr c,ge_shoot
 call enemy_screen
 ld a,(EXSCREEN)
 ld c,a
 ld a,(PX)
 sub c
 call absolute
 cp #26
 jr nc,ge_remove
 ld a,(EYSCREEN)
 ld c,a
 ld a,(PY)
 sub c
 call absolute
 cp #32
 call c,damage
ge_remove:
 ld 0(ix),#0
 jr ge_next
ge_shoot:
 dec 7(ix)
 jr nz,ge_next
 ld 7(ix),#19
 ld a,(BOSS)
 or a
 jr z,ge_fire_ready
 ld a,(CUR)
 or a
 jr nz,ge_fire_ready
 ld a,(STAGE)
 cp #2
 jr z,ge_fire_ready
 ; Short attack bursts separated by readable evasion windows.
 ld 7(ix),#18
 ld a,(TICK)
 and #63
 cp #36
 jr nc,ge_fire_ready
 ld 7(ix),#7
ge_fire_ready:
 call enemy_shot
ge_next:
 ld de,#16
 add ix,de
 ld a,(CUR)
 inc a
 ld (CUR),a
 cp #4
 jp c,ge_loop
 call player_attack
 call update_shots
 call update_missile
 ret
random:
 ld a,(RNG)
 add a,a
 jr nc,rand_ok
 xor #0x1D
rand_ok:
 ld (RNG),a
 ret
absolute:
 bit 7,a
 ret z
 neg
 ret
damage:
 ld a,(INV)
 or a
 ret nz
 ld a,#4
 call queue_sfx
 ld a,#20
 ld (INV),a
 ld a,(SH)
 dec a
 ld (SH),a
 ret nz
 ld a,#2
 ld (GS),a
 ret
enemy_shot:
 push ix
 pop hl
 ld iy,#BBASE
 ld b,#8
es_find:
 ld a,0(iy)
 or a
 jr z,es_set
 ld de,#8
 add iy,de
 djnz es_find
 ret
es_set:
 call enemy_screen
 ld 0(iy),#1
 ld a,(EXSCREEN)
 ld 1(iy),a
 ld a,(EYSCREEN)
 ld 2(iy),a
 ; Aim once at the player's launch-time position. Q4 velocities keep
 ; shallow and upward trajectories accurate without homing after launch.
 ld a,(EXSCREEN)
 ld b,a
 ld a,(PX)
 sub b
 jr nc,es_absx
 neg
es_absx:
 ld c,a
 ld a,(EYSCREEN)
 ld b,a
 ld a,(PY)
 sub b
 jr nc,es_absy
 neg
es_absy:
 cp c
 jr nc,es_max
 ld a,c
es_max:
 or a
 jr nz,es_nonzero
 inc a
es_nonzero:
 ld c,a
 ld a,(EXSCREEN)
 ld b,a
 ld a,(PX)
 call aim_velocity
 ld 3(iy),a
 ld a,(EYSCREEN)
 ld b,a
 ld a,(PY)
 call aim_velocity
 ld 4(iy),a
 ld 5(iy),#0
 ld 6(iy),#0
 ret
; A target, B origin, C longest axis. Return signed Q4 speed (max 4px).
aim_velocity:
 sub b
 ld d,#0
 jr nc,av_positive
 neg
 inc d
av_positive:
 push de
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld e,c
 ld d,#0
 ld b,#0
av_divide:
 or a
 sbc hl,de
 jr c,av_ready
 inc b
 jr av_divide
av_ready:
 pop de
 ld a,d
 or a
 ld a,b
 ret z
 neg
 ret
; A fraction, B signed Q4 velocity. Return A fraction and E pixel delta.
shot_subpixel:
 ld l,a
 ld h,#0
 ld e,b
 ld a,b
 add a,a
 sbc a,a
 ld d,a
 add hl,de
 ld a,l
 and #15
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 ld e,l
 ret
update_shots:
 ld iy,#BBASE
 ld b,#8
us_loop:
 push bc
 ld a,0(iy)
 or a
 jr z,us_next
 ld a,5(iy)
 ld b,3(iy)
 call shot_subpixel
 ld 5(iy),a
 ld a,1(iy)
 add a,e
 ld 1(iy),a
 cp #8
 jr c,us_remove
 cp #248
 jr nc,us_remove
 ld a,6(iy)
 ld b,4(iy)
 call shot_subpixel
 ld 6(iy),a
 ld a,2(iy)
 add a,e
 ld 2(iy),a
 cp #16
 jr c,us_remove
 cp #191
 jr nc,us_remove
 ld a,(PX)
 sub 1(iy)
 call absolute
 cp #12
 jr nc,us_next
 ld a,(PY)
 sub 2(iy)
 call absolute
 cp #10
 jr nc,us_next
 push bc
 call damage
 pop bc
us_remove:
 ld 0(iy),#0
us_next:
 pop bc
 ld de,#8
 add iy,de
 djnz us_loop
 ret
player_attack:
 ld a,#255
 ld (LOCK),a
 ld ix,#EBASE
 xor a
 ld (CUR),a
pa_loop:
 ld a,0(ix)
 or a
 jr z,pa_next
 ld a,(PX)
 sub 1(ix)
 call absolute
 cp #26
 jr nc,pa_next
 ld a,(PY)
 sub #55
 sub 2(ix)
 call absolute
 cp #27
 jr nc,pa_next
 ld a,(CUR)
 ld (LOCK),a
 ; X gives lock-on priority while a missile is available or in flight.
 ld a,(MISS)
 or a
 jr z,pa_gun
 ld a,(AMMO)
 ld b,a
 ld a,(MLIFE)
 or b
 jr nz,pa_next
pa_gun:
 ld a,(FIRE)
 or a
 jr z,pa_next
 ld a,(COOL)
 or a
 jr nz,pa_next
 ld a,#4
 ld (COOL),a
 ld a,(KILLS)
 cp #8
 jr c,pa_single
 dec 4(ix)
 jr z,pa_destroy
pa_single:
 dec 4(ix)
 jr nz,pa_next
pa_destroy:
 call kill_enemy
pa_next:
 ld de,#16
 add ix,de
 ld a,(CUR)
 inc a
 ld (CUR),a
 cp #4
 jr c,pa_loop
 ld a,(LOCK)
 cp #255
 jr nz,pa_lock
 xor a
 ld (LOCKN),a
 ret
pa_lock:
 ld a,(LASTLOCK)
 ld b,a
 ld a,(LOCK)
 ld (LASTLOCK),a
 cp b
 jr z,pa_same
 xor a
 ld (LOCKN),a
pa_same:
 ld a,(LOCKN)
 cp #4
 jr nc,pa_launch
 inc a
 ld (LOCKN),a
 ret
pa_launch:
 ld a,(MISS)
 or a
 ret z
 ld a,(MLIFE)
 or a
 ret nz
 ld a,(AMMO)
 or a
 ret z
 dec a
 ld (AMMO),a
 ld a,#6
 call queue_sfx
 ld a,(LOCK)
 ld (MTARGET),a
 ld a,#18
 ld (INV),a
 ld (MLIFE),a
 ld a,(PX)
 ld (MX),a
 ld a,(PY)
 sub #16
 ld (MY),a
 ld hl,#MTRAIL
 ld b,#4
missile_tail_init:
 ld a,(MX)
 ld (hl),a
 inc hl
 ld a,(MY)
 ld (hl),a
 inc hl
 djnz missile_tail_init
 call salvo_init
 xor a
 ld (LOCKN),a
 ret
kill_enemy:
 ld a,#4
 call queue_sfx
 call enemy_screen
 ld 0(ix),#0
 ld a,(EXSCREEN)
 ld (FX),a
 ld a,(EYSCREEN)
 ld (FY),a
 ld a,#12
 ld (FLASH),a
 ld a,(KILLS)
 inc a
 ld (KILLS),a
 and #3
 jr nz,ke_boss
 ld a,(SH)
 cp #8
 jr nc,ke_ammo
 inc a
 ld (SH),a
ke_ammo:
 ld a,(AMMO)
 cp #3
 jr nc,ke_boss
 inc a
 ld (AMMO),a
ke_boss:
 ld a,(BOSS)
 or a
 ret z
 ld a,(CUR)
 or a
 ret nz
 ld a,(FX)
 ld (BCX),a
 ld a,(FY)
 ld (BCY),a
 ld a,#32
 ld (BDEATH),a
 ld a,#5
 ld (GS),a
 xor a
 ld (MLIFE),a
 ld (EBASE+16),a
 ld (EBASE+32),a
 ld (EBASE+48),a
 ret
boss_death_tick:
 ld hl,#BDEATH
 dec (hl)
 jr z,boss_death_done
 ld a,(hl)
 and #7
 ret nz
 ld a,#6
 jp queue_sfx
boss_death_done:
 ld a,(STAGE)
 cp #3
 jr z,mission_complete
 inc a
 ld (STAGE),a
 ld a,#4
 ld (GS),a
 ld a,#55
 ld (TRANSITION),a
 ret
mission_complete:
 ld a,#3
 ld (GS),a
 ret
update_one_missile:
 ld a,(MLIFE)
 or a
 ret z
 dec a
 ld (MLIFE),a
um_resolve:
 ld a,(MTARGET)
 ld (CUR),a
 add a,a
 add a,a
 add a,a
 add a,a
 ld e,a
 ld d,#0
 ld ix,#EBASE
 add ix,de
 ld a,0(ix)
 or a
 jr nz,um_move
 xor a
 ld (0xE541),a
 call nearest_missile_target
 cp #255
 jr nz,um_reacquired
 xor a
 ld (MLIFE),a
 ret
um_reacquired:
 ld (MTARGET),a
 jp um_resolve
um_move:
 ld hl,#MTRAIL+5
 ld de,#MTRAIL+7
 ld bc,#6
 lddr
 ld a,(MX)
 ld (MTRAIL),a
 ld a,(MY)
 ld (MTRAIL+1),a
 call enemy_screen
 ld a,(EXSCREEN)
 ld b,a
 ld a,(MX)
 call missile_approach
 ld (MX),a
 ld a,(EYSCREEN)
 ld b,a
 ld a,(MY)
 call missile_approach
 ld (MY),a
 ld a,(MLIFE)
 or a
 jr z,um_impact
 ret nz
um_impact:
 ; Impact shockwave clears hostile projectiles for a tactical opening.
 ld iy,#BBASE
 ld b,#8
um_clear_shots:
 ld 0(iy),#0
 ld de,#8
 add iy,de
 djnz um_clear_shots
 ld a,4(ix)
 sub #8
 jr c,um_kill
 jr z,um_kill
 ld 4(ix),a
 call enemy_screen
 ld a,(EXSCREEN)
 ld (FX),a
 ld a,(EYSCREEN)
 ld (FY),a
 ld a,#12
 ld (FLASH),a
 ld a,#4
 jp queue_sfx
um_kill:
 jp kill_enemy
approach:
 ; Existing pulse easing, with signed subtraction and no missile speed cap.
 ld e,a
 ld d,#0
 ld l,b
 ld h,#0
 or a
 sbc hl,de
 sra h
 rr l
 sra h
 rr l
 add hl,de
 ld a,l
 ret
missile_approach:
 ; Signed 16-bit displacement: opposing screen edges must not wrap at 128.
 ld e,a
 ld d,#0
 ld l,b
 ld h,#0
 or a
 sbc hl,de
 sra h
 rr l
 sra h
 rr l
 bit 7,h
 jr nz,approach_negative
 ld a,l
 cp #13
 jr c,approach_add
 ld hl,#12
 jr approach_add
approach_negative:
 ld a,l
 cp #244
 jr nc,approach_add
 ld hl,#-12
approach_add:
 add hl,de
 ld a,l
 ret
; Convert signed pixel delta A, depth factor C into world coordinate HL.
world:
 ld b,#0
 bit 7,a
 jr z,world_pos
 neg
 inc b
world_pos:
 ld e,a
 ld d,#0
 ld hl,#0
 ld a,c
 ld c,#8
wmul:
 rrca
 jr nc,wmul_skip
 add hl,de
wmul_skip:
 sla e
 rl d
 dec c
 jr nz,wmul
 ld a,b
 or a
 jr z,wshift
 xor a
 sub l
 ld l,a
 sbc a,a
 sub h
 ld h,a
wshift:
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 ret
make_poses:
 ld hl,#REC
 ld de,#REC+1
 ld bc,#143
 ld (hl),#0
 ldir
 ld hl,#REC+506
 ld b,#6
mp_hide:
 ld (hl),#255
 inc hl
 djnz mp_hide
 ld ix,#EBASE
 ld iy,#REC
 xor a
 ld (CUR),a
mp_loop:
 ld a,0(ix)
 or a
 jp z,mp_next
 ld a,5(ix)
 ld hl,#REC+506
 ld e,a
 ld a,(CUR)
 ld c,a
 ld b,#0
 add hl,bc
 ld (hl),e
 ; Rotate attacking craft slightly with their lateral direction.
 ld hl,#enemy_matrix
 ld a,6(ix)
 or a
 jr z,mp_matrix
 ld hl,#enemy_matrix_right
mp_matrix:
 ld a,5(ix)
 cp #6
 jr nz,mp_matrix_copy
 ld hl,#RIVALMAT
mp_matrix_copy:
 push iy
 pop de
 ld bc,#18
 ldir
 ld a,(STAGE)
 cp #3
 jr z,mp_depth
 ld a,(BOSS)
 or a
 jr z,mp_depth
 ld a,(CUR)
 or a
 jr nz,mp_depth
 push iy
 pop hl
 ld b,#9
mp_bossscale:
 sla (hl)
 inc hl
 rl (hl)
 inc hl
 djnz mp_bossscale
mp_depth:
 call enemy_screen
 ld a,3(ix)
 neg
 ld c,a
 push bc
 ld a,(EXSCREEN)
 sub #128
 call world
 ld 18(iy),l
 ld 19(iy),h
 pop bc
 push bc
 ld a,(EYSCREEN)
 ld b,a
 ld a,#106
 sub b
 call world
 ld 20(iy),l
 ld 21(iy),h
 pop bc
 ld l,c
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 ld 22(iy),l
 ld 23(iy),h
mp_next:
 ld de,#16
 add ix,de
 ld de,#24
 add iy,de
 ld a,(CUR)
 inc a
 ld (CUR),a
 cp #4
 jp c,mp_loop
 ld iy,#REC+120
 ld a,#63
 ld (0x6000),a
 ld a,(PITCHANGLE)
 ld l,a
 ld h,#0
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,de
 ld a,(BANKANGLE)
 ld e,a
 ld d,#0
 add hl,de
 ; index * 18
 add hl,hl
 ld e,l
 ld d,h
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,de
 ld de,#0x4000
 add hl,de
mp_player:
 push iy
 pop de
 ld bc,#18
 ldir
 ld a,(PX)
 sub #128
 ld c,#48
 call world
 ld (REC+138),hl
 ld a,#106
 ld b,a
 ld a,(PY)
 ld c,a
 ld a,b
 sub c
 ld c,#48
 call world
 ld (REC+140),hl
 ld hl,#384
 ld (REC+142),hl
 xor a
 ld (REC+511),a
 ret
; Draw a LINE from LX,LY to RX,RY, using colour COL.
segment:
 call waitce
 ld hl,#CMD
 ld b,#11
sg_clear:
 ld (hl),#0
 inc hl
 djnz sg_clear
 ld a,(LX)
 ld (CMD),a
 ld a,(LY)
 ld (CMD+2),a
 ld a,(PAGE)
 ld (CMD+3),a
 ld a,(COL)
 ld (CMD+8),a
 ld c,#0
 ld a,(LX)
 ld b,a
 ld a,(RX)
 sub b
 jr nc,sg_x
 neg
 set 2,c
sg_x:
 ld d,a
 ld a,(LY)
 ld b,a
 ld a,(RY)
 sub b
 jr nc,sg_y
 neg
 set 3,c
sg_y:
 ld e,a
 cp d
 jr c,sg_major
 set 0,c
 ld a,d
 ld d,e
 ld e,a
sg_major:
 ld a,d
 ld (CMD+4),a
 ld a,e
 ld (CMD+6),a
 ld a,c
 ld (CMD+9),a
 ld a,#0x70
 ld (CMD+10),a
 ld a,#36
 ld b,#17
 call wreg
 ld hl,#CMD
 ld bc,#0x0B9B
 otir
 ret
copy_hud:
 call load15
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
game_draw:
 ld hl,#game_top
 call copy_hud
 ld hl,#game_bottom
 call copy_hud
 ; Shield and ammunition meters; zero width is not a no-op on this VDP.
 ld a,(SH)
 or a
 jr z,gd_ammo
 ld a,(SH)
 add a,a
 add a,a
 add a,a
 ld (CMD+8),a
 ld hl,#shieldbar
 call load15
 ld a,(SH)
 add a,a
 add a,a
 add a,a
 ld (CMD+8),a
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
gd_ammo:
 ld a,(AMMO)
 or a
 jr z,gd_kills
 ld hl,#ammo_bar
 call load15
 ld a,(AMMO)
 add a,a
 add a,a
 add a,a
 ld (CMD+8),a
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
gd_kills:
 ; Display 100 points per defeat; retain existing combat/progression state.
 ld a,(KILLS)
 ld b,#0
gd_hundreds:
 cp #100
 jr c,gd_hundred_digit
 sub #100
 inc b
 jr gd_hundreds
gd_hundred_digit:
 push af
 ld a,b
 ld e,#220
 call digit
 pop af
 ld b,#0
gd_tens:
 cp #10
 jr c,gd_digits
 sub #10
 inc b
 jr gd_tens
gd_digits:
 push af
 ld a,b
 ld e,#226
 call digit
 pop af
 ld e,#232
 call digit
 xor a
 ld e,#238
 call digit
 xor a
 ld e,#244
 call digit
 ld a,(STAGE)
 ld e,#172
 call digit
 ld a,(GS)
 cp #5
 jp z,boss_death_draw
 cp #4
 jp z,stage_overlay
 cp #1
 jp nz,gd_overlay
 ld a,(PAUSED)
 or a
 jp nz,gd_overlay
 ; No permanent centre sight; target acquisition and lock brackets remain.
 call draw_pulses
gd_bullets:
 ld iy,#BBASE
 ld b,#8
gd_bloop:
 ld a,0(iy)
 or a
 jr z,gd_bnext
 push bc
 ld a,1(iy)
 ld (RX),a
 ld a,3(iy)
 sra a
 sra a
 sra a
 ld c,a
 ld a,1(iy)
 sub c
 ld (LX),a
 ld a,2(iy)
 ld (RY),a
 ld a,4(iy)
 sra a
 sra a
 sra a
 ld c,a
 ld a,2(iy)
 sub c
 ld (LY),a
 ld a,#14
 ld (COL),a
 call segment
 pop bc
gd_bnext:
 ld de,#8
 add iy,de
 djnz gd_bloop
 ld a,(MLIFE)
 or a
 jr z,gd_lock
 call salvo_draw
 jp gd_lock
gd_lock:
 ld a,(LOCK)
 cp #255
 jp z,gd_flash
 add a,a
 add a,a
 add a,a
 add a,a
 ld e,a
 ld d,#0
 ld ix,#EBASE
 add ix,de
 call enemy_screen
 ld a,(EXSCREEN)
 ld (SXC),a
 ld a,(EYSCREEN)
 ld (SYC),a
 ld a,#13
 ld (COL),a
 ; Match the demo's asymmetric open brackets and target health strip.
 ld iy,#demo_acquire
 ld a,(LOCKN)
 cp #4
 jr c,gd_target_shape
 ld a,#14
 ld (COL),a
 ld iy,#demo_locked
gd_target_shape:
 ld a,#4
 call sight
 ld a,(SXC)
 sub #16
 ld (LX),a
 add a,#32
 ld (RX),a
 ld a,(SYC)
 sub #15
 ld (LY),a
 ld (RY),a
 ld a,#3
 ld (COL),a
 call segment
 ld a,5(ix)
 inc a
 ld e,a
 ld a,(BOSS)
 or a
 jr z,target_hp_normal
 ld a,(LOCK)
 or a
 jr nz,target_hp_normal
 ld e,#72
 ld a,5(ix)
 cp #5
 jr nz,target_hp_white
 ld e,#64
 jr target_hp_normal
target_hp_white:
 cp #6
 jr nz,target_hp_normal
 ld e,#160
target_hp_normal:
 ld d,#0
 ld l,4(ix)
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld c,#0
target_hp_div:
 or a
 sbc hl,de
 jr c,target_hp_done
 inc c
 jr target_hp_div
target_hp_done:
 ld a,(LX)
 add a,c
 ld (RX),a
 ld a,#13
 ld (COL),a
 call segment
 jp gd_flash
gd_flash:
 ld a,(FLASH)
 or a
 jr z,gd_shield
 dec a
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#explosion_frames
 add hl,de
 push hl
 pop iy
 ld a,(FX)
 cp #25
 jr nc,blast_xmax
 ld a,#25
blast_xmax:
 cp #231
 jr c,blast_xready
 ld a,#230
blast_xready:
 ld (SXC),a
 ld a,(FY)
 cp #40
 jr nc,blast_ymax
 ld a,#40
blast_ymax:
 cp #175
 jr c,blast_yready
 ld a,#174
blast_yready:
 ld (SYC),a
 ld a,(FLASH)
 cp #9
 ld a,#15
 jr nc,blast_color
 ld a,#14
blast_color:
 ld (COL),a
 ld a,#8
 ld (SCNT),a
 call sight
gd_shield:
 ld a,(INV)
 or a
 jr z,gd_boss
 ld a,(PX)
 ld (SXC),a
 ld a,(PY)
 ld (SYC),a
 ld a,#13
 ld (COL),a
 ld iy,#shield_segments
 ld a,#4
 call sight
 jp gd_boss
shield_segments:
 .db -24,-10,-19,-16, 19,-16,24,-10
 .db -24,10,-19,16, 19,16,24,10

gd_boss:
 ld a,(BOSS)
 or a
 ret z
 ld a,#80
 ld (LX),a
 ld a,(STAGE)
 cp #3
 ld a,(EBASE+4)
 jr z,gd_hpwidth
 add a,a
gd_hpwidth:
 add a,#80
 ld (RX),a
 ld a,#20
 ld (LY),a
 ld (RY),a
 ld a,#14
 ld (COL),a
 jp segment
gd_overlay:
 ld hl,#overlay
 call load15
 ld a,(GS)
 or a
 ld hl,#812
 jr z,gd_ovready
 cp #2
 ld hl,#812
 jr z,gd_ovready
 cp #3
 ld hl,#852
 jr z,gd_ovready
 ld hl,#892
gd_ovready:
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
digit:
 push de
 add a,a
 add a,a
 add a,a
 push af
 ld hl,#digit_cmd
 call load15
 pop af
 ld (CMD),a
 pop de
 ld a,e
 ld (CMD+4),a
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
game_top:
 .dw 0,768,0,0,256,14
 .db 0,0,0xD0
game_bottom:
 .dw 0,782,0,198,256,14
 .db 0,0,0xD0
ammo_bar:
 .dw 0,0,115,202,24,6
 .db 14,0,0xC0
digit_cmd:
 .dw 0,800,220,2,6,10
 .db 0,0,0xD0
overlay:
 .dw 0,812,0,76,256,30
 .db 0,0,0xD0
directions:
 .db 0,252,3,253,4,0,3,3,0,4,253,3,252,0,253,253
.include "game_tables.inc"

SXC=0xE528
SYC=0xE529
SCNT=0xE52A
SRAD=0xE52B
sight:
 ld (SCNT),a
sight_next:
 ld a,(SXC)
 add a,0(iy)
 ld (LX),a
 ld a,(SYC)
 add a,1(iy)
 ld (LY),a
 ld a,(SXC)
 add a,2(iy)
 ld (RX),a
 ld a,(SYC)
 add a,3(iy)
 ld (RY),a
 call segment
 ld de,#4
 add iy,de
 ld hl,#SCNT
 dec (hl)
 jr nz,sight_next
 ret
aim_segments:
 .db -17,-9,-17,-3, -17,-9,-10,-9
 .db 17,-9,17,-3, 17,-9,10,-9
 .db -12,9,-5,9, 12,9,5,9
 .db -3,0,0,-3, 0,-3,3,0
lock_segments:
 .db -20,-17,-20,-8, -20,-17,-11,-17
 .db 20,-17,20,-8, 20,-17,11,-17
 .db -20,17,-20,8, -20,17,-11,17
 .db 20,17,20,8, 20,17,11,17

outer_ring:
 .db 31,2,28,13,26,18,18,26,13,28,2,31,-2,31,-13,28,-18,26,-26,18,-28,13,-31,2,-31,-2,-28,-13,-26,-18,-18,-26,-13,-28,-2,-31,2,-31,13,-28,18,-26,26,-18,28,-13,31,-2
inner_ring:
 .db 7,0,6,3,6,4,4,6,3,6,0,7,0,7,-3,6,-4,6,-6,4,-6,3,-7,0,-7,0,-6,-3,-6,-4,-4,-6,-3,-6,0,-7,0,-7,3,-6,4,-6,6,-4,6,-3,7,0
acquire_wide:
 .db -27,-27,-20,-27,-27,-27,-27,-20,27,-27,20,-27,27,-27,27,-20,-27,27,-20,27,-27,27,-27,20,27,27,20,27,27,27,27,20
acquire_mid:
 .db -23,-23,-16,-23,-23,-23,-23,-16,23,-23,16,-23,23,-23,23,-16,-23,23,-16,23,-23,23,-23,16,23,23,16,23,23,23,23,16
acquire_tight:
 .db -19,-19,-12,-19,-19,-19,-19,-12,19,-19,12,-19,19,-19,19,-12,-19,19,-12,19,-19,19,-19,12,19,19,12,19,19,19,19,12

BANKANGLE=0xE52C
PITCHANGLE=0xE52D
VCOOL=0xE52E
VPULSE=0xE680
visual_tick:
 ld a,(DIR)
 ld b,#8
 cp #2
 jr c,vt_bank
 cp #5
 jr nc,vt_left
 ld b,#16
 jr vt_bank
vt_left:
 cp #6
 jr c,vt_bank
 ld b,#0
vt_bank:
 ld hl,#BANKANGLE
 call ease_angle
 ld a,(DIR)
 ld b,#4
 cp #1
 jr z,vt_up
 cp #2
 jr z,vt_up
 cp #8
 jr z,vt_up
 cp #4
 jr z,vt_down
 cp #5
 jr z,vt_down
 cp #6
 jr nz,vt_pitch
vt_down:
 ld b,#0
 jr vt_pitch
vt_up:
 ld b,#8
vt_pitch:
 ld hl,#PITCHANGLE
 call ease_angle
 ld ix,#VPULSE
 ld b,#4
vt_age:
 ld a,0(ix)
 or a
 jr z,vt_anext
 dec 0(ix)
 push bc
 ld a,1(ix)
 ld b,#128
 call approach
 ld 1(ix),a
 ld a,2(ix)
 ld b,#90
 call approach
 ld 2(ix),a
 pop bc
vt_anext:
 ld de,#4
 add ix,de
 djnz vt_age
 ld a,(VCOOL)
 or a
 jr z,vt_shoot
 dec a
 ld (VCOOL),a
 ret
vt_shoot:
 ld a,(FIRE)
 or a
 ret z
 ld a,#3
 ld (VCOOL),a
 ld ix,#VPULSE
 ld b,#4
vt_slot:
 ld a,0(ix)
 or a
 jr z,vt_new
 ld de,#4
 add ix,de
 djnz vt_slot
 ret
vt_new:
 ld a,#1
 call queue_sfx
 ld 0(ix),#6
 ld a,(PX)
 ld 1(ix),a
 ld a,(PY)
 ld 2(ix),a
 ret
ease_angle:
 ld a,(hl)
 cp b
 ret z
 jr c,ease_up
 dec (hl)
 ret
ease_up:
 inc (hl)
 ret
draw_pulses:
 ld ix,#VPULSE
 ld a,#4
 ld (SCNT),a
dp_loop:
 ld a,0(ix)
 or a
 jr z,dp_next
 ld b,a
 ld a,#6
 sub b
 add a,a
 add a,a
 ld e,a
 ld d,#0
 ld hl,#pulse_shape
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,(hl)
 ld (SRAD),a
 inc hl
 ld a,(hl)
 ld (COL),a
 ld a,2(ix)
 sub #7
 ld (LY),a
 ld b,a
 ld a,(SRAD)
 add a,b
 ld (RY),a
 ld a,1(ix)
 sub e
 ld (LX),a
 ld (RX),a
 push de
 call segment
 pop de
 ld a,1(ix)
 add a,e
 ld (LX),a
 ld (RX),a
 call segment
dp_next:
 ld de,#4
 add ix,de
 ld hl,#SCNT
 dec (hl)
 jr nz,dp_loop
 ret
pulse_shape:
 ; separation, distance from launch, pulse length, colour
 .db 15,13,6,15, 10,28,5,13, 6,40,4,13
 .db 3,49,3,13, 1,55,2,10, 0,59,1,10
speed_streaks:
 ld a,(GS)
 cp #1
 ret nz
 ld a,#63
 ld (0x6000),a
 ld a,(TICK)
 and #63
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x5000
 add hl,de
 push hl
 pop iy
 ld a,#8
 ld (SCNT),a
ss_loop:
 ld a,0(iy)
 ld (LX),a
 ld a,1(iy)
 ld (LY),a
 ld a,2(iy)
 ld (RX),a
 ld a,3(iy)
 ld (RY),a
 ld a,#4
 ld (COL),a
 call segment
 ld de,#4
 add iy,de
 ld hl,#SCNT
 dec (hl)
 jr nz,ss_loop
 jp waitce

EXSCREEN=0xE530
EYSCREEN=0xE531
enemy_screen:
 ld l,1(ix)
 ld h,#0
 ld a,(PX)
 ld e,a
 ld d,#0
 or a
 sbc hl,de
 ld de,#128
 add hl,de
 ld b,#24
 ld c,#232
 call clip_screen
 ld (EXSCREEN),a
 ld l,2(ix)
 ld h,#0
 ld a,(PY)
 ld e,a
 ld d,#0
 or a
 sbc hl,de
 ld de,#145
 add hl,de
 ld b,#32
 ld c,#181
 call clip_screen
 ld (EYSCREEN),a
 ret
clip_screen:
 bit 7,h
 jr nz,cs_low
 ld a,h
 or a
 jr nz,cs_high
 ld a,l
 cp b
 jr c,cs_low
 cp c
 ret c
cs_high:
 ld a,c
 ret
cs_low:
 ld a,b
 ret
steer_sky:
 ld a,(PX)
 sub #128
 sra a
 sra a
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ld hl,(SKY)
 add hl,de
 ld (SKY),hl
 ld a,(PY)
 sub #145
 sra a
 sra a
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ld hl,(SKY+2)
 add hl,de
 ld (SKY+2),hl
 ret
steer_wall:
 ld a,#128
 ld b,a
 ld a,(PX)
 ld c,a
 ld a,b
 sub c
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ex de,hl
 add hl,hl
 ex de,hl
 ld hl,(WALL+18)
 add hl,de
 ld (WALL+18),hl
 ld a,(PY)
 sub #145
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ex de,hl
 add hl,hl
 ex de,hl
 ld hl,(WALL+20)
 add hl,de
 ld (WALL+20),hl
 ret

; Temporary PSG sound design for the interactive development demo.
SFX_PENDING=0xE532
queue_sfx:
 push bc
 ld b,a
 ld a,(SFX_PENDING)
 cp b
 jr nc,qs_done
 ld a,b
 ld (SFX_PENDING),a
qs_done:
 pop bc
 ret
soundstep:
 ld a,(PAUSED)
 or a
 jr nz,sfx_mute
 ld a,(SFX_PENDING)
 or a
 jr z,sound_decay
 ld b,a
 xor a
 ld (SFX_PENDING),a
 ld a,b
 cp #1
 jr nz,sfx_accept
 ld a,(SOUND)
 cp #5
 jr nc,sound_decay
 ld a,b
sfx_accept:
 ld (SOUND_KIND),a
 cp #1
 ld a,#4
 jr z,sfx_length
 ld a,#7
sfx_length:
 ld (SOUND),a
sound_decay:
 ld a,(SOUND)
 or a
 ret z
 dec a
 ld (SOUND),a
 ld e,a
 ld a,#8
 out (0xA0),a
 ld a,e
 or a
 jr z,sfx_volume_ready
 add a,#5
sfx_volume_ready:
 out (0xA1),a
sound_noise:
 ld a,#7
 out (0xA0),a
 ld a,#0xB7
 out (0xA1),a
 ld a,#6
 out (0xA0),a
 ld a,(SOUND_KIND)
 cp #4
 ld a,#5
 jr nz,sfx_noise_pitch
 ld a,#24
sfx_noise_pitch:
 out (0xA1),a
 ret
sfx_mute:
 xor a
 ld (SOUND),a
 ld (SFX_PENDING),a
 ld a,#8
 out (0xA0),a
 xor a
 out (0xA1),a
 ret

boss_motion:
 ld a,(STAGE)
 cp #3
 jr z,white_raven_motion
 cp #2
 jr nz,outer_guard_motion
 ; Reactor core keeps moving even during a prolonged fight.
 call outer_guard_motion
 ld a,1(ix)
 sub #128
 sra a
 add a,#128
 ld 1(ix),a
 ld a,2(ix)
 add a,#3
 ld 2(ix),a
 ld a,3(ix)
 sub #135
 sra a
 add a,#140
 ld 3(ix),a
 ret
outer_guard_motion:
 ld a,(TICK)
 srl a
 and #63
 ld e,a
 ld d,#0
 ld hl,#sine
 add hl,de
 ld a,(hl)
 add a,#128
 ld 1(ix),a
 ld a,(TICK)
 srl a
 add a,#16
 and #63
 ld e,a
 ld hl,#sine
 add hl,de
 ld a,(hl)
 sra a
 sra a
 add a,#60
 ld 2(ix),a
 ld a,(TICK)
 srl a
 add a,#32
 and #63
 ld e,a
 ld hl,#sine
 add hl,de
 ld a,(hl)
 sra a
 add a,#135
 ld 3(ix),a
 ret
white_raven_motion:
 ld a,#17
 ld (0x6000),a
 ld hl,(TICK)
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x4000
 add hl,de
 ld de,#RIVALMAT
 ld bc,#18
 ldir
 ld a,(hl)
 ld 1(ix),a
 inc hl
 ld a,(hl)
 ld 2(ix),a
 inc hl
 ld a,(hl)
 ld 3(ix),a
 ; Reaction to an incoming guided missile: a lateral break, sometimes defeating it.
 ld a,(MLIFE)
 or a
 ret z
 ld a,1(ix)
 add a,#12
 ld 1(ix),a
 ld a,(MLIFE)
 cp #8
 ret nz
 ld a,(TICK)
 bit 5,a
 ret z
 xor a
 ld (MLIFE),a
 ret
interior_sky:
 ret
interior_transform:
 ld a,(STAGE)
 cp #2
 ret nz
 ld hl,#interior_identity
 ld de,#WALL
 ld bc,#24
 ldir
 ; Corridor geometry moves continuously into the wider chamber.
 call interior_tick
 add hl,hl
 add hl,hl
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,de
 add hl,hl
it_mod:
 ld de,#320
 or a
 sbc hl,de
 jr nc,it_mod
 add hl,de
 ex de,hl
 ld hl,#180
 or a
 sbc hl,de
 ld (WALL+22),hl
 ld hl,#0
 ld (WALL+24),hl
 ld (WALL+26),hl
 ld hl,#320
 ld (WALL+28),hl
 ld a,#31
 ld (WALL+31),a
 ret
interior_identity:
 .dw 16384,0,0,0,16384,0,0,0,16384,0,0,0
interior_bank:
 ; Restore the original corridor; omit only subpixel detail in distant modules.
 call interior_tick
 srl h
 rr l
 srl h
 rr l
 srl h
 rr l
 ld a,(WCOUNT)
 dec a
 ld e,a
 ld d,#0
 add hl,de
 ld de,#36
 or a
 sbc hl,de
 ld a,#5
 jp nc,wall_bank_selected
 ld a,(WCOUNT)
 cp #4
 ld a,#36
 jp nc,wall_bank_selected
 ld a,#4
 jp wall_bank_selected
interior_tick:
 ld hl,#0
 ld a,(GS)
 cp #4
 ret z
 ld hl,(TICK)
 ret
stage_overlay:
 ld hl,#stage_card
 call load15
 ld a,(STAGE)
 dec a
 ld b,a
 ld hl,#922
 ld de,#30
sc_row:
 ld a,b
 or a
 jr z,sc_ready
 add hl,de
 dec b
 jr sc_row
sc_ready:
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
stage_card:
 .dw 0,922,0,80,256,30
 .db 0,0,0xD0
interior_clear:
 ld hl,#interior_fill
 call load15
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
interior_fill:
 .dw 0,0,0,14,256,184
 .db 0,0,0xC0

; Twelve frames: hot core, expanding irregular debris, fading sparks.
explosion_frames:
 .db 20,3,21,3,4,16,4,17,-13,12,-14,13,-19,-5,-20,-5,-7,-15,-7,-16,15,-11,16,-11,0,-1,0,-1,0,1,0,1
 .db 18,3,19,3,4,15,4,15,-12,11,-13,12,-18,-5,-18,-5,-6,-14,-7,-15,14,-10,15,-10,0,-1,0,-1,0,1,0,1
 .db 17,2,18,3,3,13,3,14,-11,10,-12,11,-16,-4,-17,-5,-6,-13,-6,-13,13,-9,13,-9,0,-1,0,-1,0,1,0,1
 .db 15,2,16,2,3,12,3,13,-10,9,-10,10,-14,-4,-15,-4,-5,-11,-5,-12,11,-8,12,-9,0,-1,0,-1,0,1,0,1
 .db 10,2,14,2,2,8,3,11,-7,6,-9,9,-10,-3,-14,-4,-4,-8,-5,-11,8,-6,11,-8,0,-1,0,-1,0,1,0,1
 .db 9,1,13,2,2,7,2,10,-6,5,-8,8,-8,-2,-12,-3,-3,-7,-4,-10,7,-5,10,-7,-1,-1,1,-1,0,1,0,1
 .db 7,1,11,2,1,6,2,9,-5,4,-7,7,-7,-2,-11,-3,-2,-5,-4,-8,5,-4,8,-6,-2,-1,2,-1,0,1,0,1
 .db 6,1,9,1,1,4,2,8,-4,3,-6,6,-5,-1,-9,-2,-2,-4,-3,-7,4,-3,7,-5,-3,-1,3,-1,-1,1,1,1
 .db 4,1,8,1,1,3,2,6,-3,2,-5,5,-4,-1,-8,-2,-1,-3,-3,-6,3,-2,6,-4,-4,-1,4,-1,-2,1,2,1
 .db 2,0,6,1,0,2,1,5,-1,1,-4,4,-2,-1,-6,-2,-1,-2,-2,-5,2,-1,5,-3,-5,-1,5,-1,-3,1,3,1
 .db 1,0,5,1,0,1,1,4,0,0,-3,3,-1,0,-4,-1,0,0,-2,-4,0,0,4,-2,-6,-1,6,-1,-4,1,4,1
 .db -1,0,3,0,0,-1,1,2,1,-1,-2,2,1,0,-3,-1,0,1,-1,-2,-1,1,2,-2,-7,-1,7,-1,-5,1,5,1

demo_acquire:
 .db -13,-10,-13,10, 13,-10,13,10, -13,-10,-5,-10, 5,10,13,10
demo_locked:
 .db -17,-10,-17,10, 17,-10,17,10, -17,-10,-5,-10, 5,10,17,10

boss_death_draw:
 ld a,#21
 ld (0x6000),a
 ld a,(BDEATH)
 dec a
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x4000
 add hl,de
 push hl
 pop iy
 ld a,(BCX)
 ld (SXC),a
 ld a,(BCY)
 ld (SYC),a
 ld a,(BDEATH)
 cp #30
 ld a,#15
 jr nc,bdcolor
 ld a,(BDEATH)
 cp #10
 ld a,#14
 jr nc,bdcolor
 ld a,#5
bdcolor:
 ld (COL),a
 ld a,#16
 ld (SCNT),a
bd_segment:
 ld a,(SXC)
 ld d,0(iy)
 ld b,#2
 ld c,#253
 call bd_point
 ld (LX),a
 ld a,(SYC)
 ld d,1(iy)
 ld b,#16
 ld c,#194
 call bd_point
 ld (LY),a
 ld a,(SXC)
 ld d,2(iy)
 ld b,#2
 ld c,#253
 call bd_point
 ld (RX),a
 ld a,(SYC)
 ld d,3(iy)
 ld b,#16
 ld c,#194
 call bd_point
 ld (RY),a
 call segment
 ld de,#4
 add iy,de
 ld hl,#SCNT
 dec (hl)
 jr nz,bd_segment
 ret
bd_point:
 ld l,a
 ld h,#0
 ld e,d
 ld a,d
 add a,a
 sbc a,a
 ld d,a
 add hl,de
 jp clip_screen

draw_missile_ribbon:
 ld a,(MOFFSET)
 ld c,a
 ld a,(MX)
 add a,c
 ld (LX),a
 ld a,(MY)
 ld (LY),a
 ld iy,#MTRAIL
 ld b,#4
missile_trail_draw:
 push bc
 ld a,(MOFFSET)
 ld c,a
 ld a,0(iy)
 add a,c
 ld (RX),a
 ld a,1(iy)
 ld (RY),a
 ; Never issue a degenerate or discontinuous trail segment.
 ld a,(LX)
 ld c,a
 ld a,(RX)
 sub c
 jr nc,mt_absx
 neg
mt_absx:
 cp #25
 jr nc,missile_trail_next
 ld d,a
 ld a,(LY)
 ld c,a
 ld a,(RY)
 sub c
 jr nc,mt_absy
 neg
mt_absy:
 cp #25
 jr nc,missile_trail_next
 or d
 jr z,missile_trail_next
 ld a,#14
 ld (COL),a
 call segment
missile_trail_next:
 ld a,(MOFFSET)
 ld c,a
 ld a,0(iy)
 add a,c
 ld (LX),a
 ld a,1(iy)
 ld (LY),a
 inc iy
 inc iy
 pop bc
 djnz missile_trail_draw
 ret

; Three independent missiles: life,x,y,target and four previous points.
; The original public combat state remains the aggregate salvo lifetime.
salvo_init:
 xor a
 ld (0xE540),a
 ld (0xE541),a
si_loop:
 call salvo_pointer
 push hl
 ld a,(0xE540)
 or a
 ld a,(LOCK)
 jr z,si_target
 call nearest_missile_target
 cp #255
 jr nz,si_target
 ld a,(LOCK)
si_target:
 ld (MTARGET),a
 ld e,a
 ld d,#0
 ld hl,#target_bits
 add hl,de
 ld a,(0xE541)
 or (hl)
 ld (0xE541),a
 ld a,(0xE540)
 ld b,a
 add a,a
 add a,b
 add a,#12
 ld (MLIFE),a
 ld a,b
 add a,a
 add a,a
 add a,a
 sub #8
 ld b,a
 ld a,(PX)
 add a,b
 ld (MX),a
 ld a,(PY)
 sub #16
 ld (MY),a
 pop de
 ld hl,#MLIFE
 ld bc,#4
 ldir
 ld b,#4
si_tail:
 ld a,(MX)
 ld (de),a
 inc de
 ld a,(MY)
 ld (de),a
 inc de
 djnz si_tail
 ld hl,#0xE540
 inc (hl)
 ld a,(hl)
 cp #3
 jr c,si_loop
 ret
salvo_pointer:
 ld a,(0xE540)
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 ld d,h
 ld e,l
 add hl,hl
 add hl,de
 ld de,#0xE6D0
 add hl,de
 ret
salvo_load:
 call salvo_pointer
 ld de,#MLIFE
 ld bc,#4
 ldir
 ld de,#MTRAIL
 ld bc,#8
 ldir
 ret
salvo_save:
 call salvo_pointer
 ex de,hl
 ld hl,#MLIFE
 ld bc,#4
 ldir
 ld hl,#MTRAIL
 ld bc,#8
 ldir
 ret
update_missile:
 ld a,(MLIFE)
 or a
 ret z
 xor a
 ld (0xE540),a
su_loop:
 call salvo_load
 call update_one_missile
 call salvo_save
 ld a,(GS)
 cp #5
 ret z
 ld hl,#0xE540
 inc (hl)
 ld a,(hl)
 cp #3
 jr c,su_loop
 ret
salvo_draw:
 xor a
 ld (0xE540),a
 ld (MOFFSET),a
sd_loop:
 call salvo_load
 ld a,(MLIFE)
 or a
 call nz,draw_missile_ribbon
 ld hl,#0xE540
 inc (hl)
 ld a,(hl)
 cp #3
 jr c,sd_loop
 ret
nearest_missile_target:
 ld a,#255
 ld (0xE543),a
 ld (0xE544),a
 xor a
 ld (CUR),a
 ld ix,#EBASE
nt_loop:
 ld a,0(ix)
 or a
 jr z,nt_next
 ld a,(CUR)
 ld e,a
 ld d,#0
 ld hl,#target_bits
 add hl,de
 ld a,(0xE541)
 and (hl)
 jr nz,nt_next
 call enemy_screen
 ld a,(EXSCREEN)
 ld b,a
 ld a,(MX)
 sub b
 jr nc,nt_x
 neg
nt_x:
 srl a
 ld c,a
 ld a,(EYSCREEN)
 ld b,a
 ld a,(MY)
 sub b
 jr nc,nt_y
 neg
nt_y:
 srl a
 add a,c
 ld b,a
 ld a,(0xE543)
 cp b
 jr c,nt_next
 ld a,b
 ld (0xE543),a
 ld a,(CUR)
 ld (0xE544),a
nt_next:
 ld de,#16
 add ix,de
 ld hl,#CUR
 inc (hl)
 ld a,(hl)
 cp #4
 jr c,nt_loop
 ld a,(0xE544)
 ret
target_bits:
 .db 1,2,4,8
