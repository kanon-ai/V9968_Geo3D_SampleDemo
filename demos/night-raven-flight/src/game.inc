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
 call game_init
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
 ld hl,(TICK)
 ld de,#900
 or a
 sbc hl,de
 jr c,gt_regular
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
 ld 4(ix),#48
 ld 5(ix),#3
 ld 6(ix),#0
 ld 7(ix),#16
gt_regular:
 ld hl,#SPAWN
 inc (hl)
 ld a,(hl)
 cp #24
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
 ld 7(ix),#28
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
 ld a,(TICK)
 rrca
 and #63
 ld e,a
 ld d,#0
 ld hl,#sine
 add hl,de
 ld a,(hl)
 add a,#128
 ld 1(ix),a
 jr ge_shoot
ge_normal:
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
 ld 7(ix),#28
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
 ld a,#24
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
 ld a,(EXSCREEN)
 ld c,a
 ld a,(PX)
 sub c
 ld 3(iy),#0
 call absolute
 cp #14
 jr c,es_dy
 ld a,(EXSCREEN)
 ld c,a
 ld a,(PX)
 cp c
 ld 3(iy),#2
 jr nc,es_dy
 ld 3(iy),#254
es_dy:
 ld 4(iy),#4
 ret
update_shots:
 ld iy,#BBASE
 ld b,#8
us_loop:
 ld a,0(iy)
 or a
 jr z,us_next
 ld a,1(iy)
 add a,3(iy)
 ld 1(iy),a
 cp #8
 jr c,us_remove
 cp #248
 jr nc,us_remove
 ld a,2(iy)
 add a,4(iy)
 ld 2(iy),a
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
 cp #10
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
 ld (MLIFE),a
 ld a,(PX)
 ld (MX),a
 ld a,(PY)
 sub #16
 ld (MY),a
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
 ld a,#3
 ld (GS),a
 ret
update_missile:
 ld a,(MLIFE)
 or a
 ret z
 dec a
 ld (MLIFE),a
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
 ld (MLIFE),a
 ret
um_move:
 call enemy_screen
 ld a,(EXSCREEN)
 ld b,a
 ld a,(MX)
 call approach
 ld (MX),a
 ld a,(EYSCREEN)
 ld b,a
 ld a,(MY)
 call approach
 ld (MY),a
 ld a,(MLIFE)
 or a
 ret nz
 ld a,4(ix)
 sub #8
 jr c,um_kill
 jr z,um_kill
 ld 4(ix),a
 ret
um_kill:
 jp kill_enemy
approach:
 ld e,a
 ld a,b
 sub e
 sra a
 sra a
 add a,e
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
 push iy
 pop de
 ld bc,#18
 ldir
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
 ; Real kill count digits from HUD atlas.
 ld a,(KILLS)
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
 ld e,#231
 call digit
 pop af
 ld e,#239
 call digit
 ld a,(GS)
 cp #1
 jp nz,gd_overlay
 ld a,(PAUSED)
 or a
 jp nz,gd_overlay
 ; Twin engines provide a stable visual reference for player thrust.
 ld a,(PX)
 sub #11
 ld (LX),a
 ld (RX),a
 ld a,(PY)
 add a,#5
 ld (LY),a
 add a,#13
 ld (RY),a
 ld a,#13
 ld (COL),a
 call segment
 ld a,(PX)
 add a,#11
 ld (LX),a
 ld (RX),a
 call segment
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
 ld (LX),a
 ld (RX),a
 ld a,2(iy)
 ld (RY),a
 sub #9
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
 ld a,(MX)
 ld (LX),a
 sub #5
 ld (RX),a
 ld a,(MY)
 ld (LY),a
 add a,#18
 ld (RY),a
 ld a,#14
 ld (COL),a
 call segment
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
 ; Target acquisition ring contracts in three readable steps.
 ld a,(LOCKN)
 cp #10
 jr nc,gd_ready
 ld iy,#acquire_wide
 cp #4
 jr c,gd_acquire
 ld iy,#acquire_mid
 cp #7
 jr c,gd_acquire
 ld iy,#acquire_tight
gd_acquire:
 ld a,#8
 call sight
 jp gd_flash
gd_ready:
 ld a,#14
 ld (COL),a
 ld iy,#lock_segments
 ld a,#8
 call sight
 ; Short ready bars above the locked target.
 ld a,(SXC)
 sub #9
 ld (LX),a
 add a,#18
 ld (RX),a
 ld a,(SYC)
 sub #23
 ld (LY),a
 ld (RY),a
 call segment
gd_flash:
 ld a,(FLASH)
 or a
 jr z,gd_shield
 ld a,(FX)
 sub #14
 ld (LX),a
 add a,#28
 ld (RX),a
 ld a,(FY)
 sub #14
 ld (LY),a
 add a,#28
 ld (RY),a
 ld a,#14
 ld (COL),a
 call segment
 ld a,(FY)
 add a,#14
 ld (LY),a
 sub #28
 ld (RY),a
 call segment
gd_shield:
 ld a,(INV)
 or a
 jr z,gd_boss
 ld a,(PX)
 sub #25
 ld (LX),a
 add a,#50
 ld (RX),a
 ld a,(PY)
 sub #18
 ld (LY),a
 ld (RY),a
 ld a,#15
 ld (COL),a
 call segment
 ld a,(PY)
 add a,#15
 ld (LY),a
 ld (RY),a
 call segment
gd_boss:
 ld a,(BOSS)
 or a
 ret z
 ld a,#80
 ld (LX),a
 ld a,(EBASE+4)
 add a,a
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
 ld hl,#866
 jr z,gd_ovready
 cp #3
 ld hl,#920
 jr z,gd_ovready
 ld hl,#974
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
 .dw 0,800,231,2,8,8
 .db 0,0,0xD0
overlay:
 .dw 0,812,0,76,256,50
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
 ld a,#10
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
 out (0xA1),a
 ld a,(SOUND_KIND)
 cp #4
 jr z,sound_noise
 cp #6
 jr z,sound_noise
 ld a,#7
 out (0xA0),a
 ld a,#0xBE
 out (0xA1),a
 xor a
 out (0xA0),a
 ld a,e
 add a,a
 add a,a
 add a,#40
 out (0xA1),a
 ld a,#1
 out (0xA0),a
 xor a
 out (0xA1),a
 ret
sound_noise:
 ld a,#7
 out (0xA0),a
 ld a,#0xB7
 out (0xA1),a
 ld a,#6
 out (0xA0),a
 ld a,#15
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
