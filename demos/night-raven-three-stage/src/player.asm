; NIGHT RAVEN - Geo3D combat showcase; resident vertices and typed faces.
.module skyweave
.area ROM (ABS)
.org 0x4000
.ascii "AB"
.dw boot,0,0,0
.ds 6
boot:
 di
 ld sp,#0xF300
 ld hl,#0x4100
 ld de,#0xC300
 ld bc,#0x1F00
 ldir
 jp start
PAGE = 0xE200
FRAME = 0xE202
REC = 0xC000
CMD = 0xE400
PTR = 0xE410
COUNT = 0xE412
DONE = 0xE420
MODEL = 0xE414
MODEL_PTR = 0xE416
SOUND = 0xE418
SOUND_KIND = 0xE419
SKY = 0xE430
WALL = 0xE450
WCOUNT = 0xE470
.org 0xC300
start:
 xor a
 ld (0xE7F0),a
 di
 ld sp,#0xF300
 call 0x0138
 rlca
 rlca
 and #3
 ld c,a
 ld b,#0
 ld hl,#0xFCC1
 add hl,bc
 ld a,(hl)
 and #0x80
 or c
 ld c,a
 inc hl
 inc hl
 inc hl
 inc hl
 ld a,(hl)
 rrca
 rrca
 rrca
 rrca
 and #12
 or c
 ld h,#0x80
 call 0x0024
 di
 in a,(0xFF)
 xor #1
 out (0xFE),a
 ld a,(0x002D)
 cp #3
 jr c,cpu_ready
 ld a,#0x81
 call 0x0180
 di
cpu_ready:
 xor a
 ld (PAGE),a
 ld hl,#0
 ld (FRAME),hl
 ld (DONE),hl
 out (0x9C),a
 ld hl,#regs
regloop:
 ld b,(hl)
 inc hl
 ld a,b
 cp #255
 jr z,regdone
 ld a,(hl)
 inc hl
 call wreg
 jr regloop
regdone:
 xor a
 ld b,#16
 call wreg
 ld hl,#palette
 ld bc,#0x209A
 otir
 ld hl,#assets8
assets8_loop:
 ld a,(hl)
 inc hl
 cp #255
 jr z,assets8_done
 ld (0x6000),a
 ld a,(hl)
 inc hl
 push hl
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x40
 out (0x99),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 pop hl
 jr assets8_loop
assets8_done:
 ld a,#0x18
 out (0x9D),a
 ld hl,#camera
 ld bc,#0x0C9F
 otir
 ld a,#1
 ld (0x6000),a
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0x400E)
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,#0x4020
 ld de,(0x400F)
 call geoblock
 ld a,#255
 ld (MODEL),a
 xor a
 ld (SOUND),a
 ; Explicitly silence PSG channels without starting any sound.
 ld a,#8
 out (0xA0),a
 xor a
 out (0xA1),a
 ld a,#9
 out (0xA0),a
 xor a
 out (0xA1),a
 ld a,#10
 out (0xA0),a
 xor a
 out (0xA1),a
 ld a,#0x40
 ld b,#1
 call wreg
 call game_init
 call fm_init
main:
 call game_tick
 call fm_poll
 call soundstep
 ; One rendered frame advances three 60-Hz simulation ticks.
 xor a
 out (0xE6),a
 ld (0xE7F1),a
 ld a,(PAGE)
 xor #1
 ld (PAGE),a
 ld a,(GS)
 or a
 jr nz,render_play
 call title_screen
 jp frame_pace
render_play:
 ; LRMM sky transform follows the same camera orientation as the scene.
 ld a,#54
 ld (0x6000),a
 ld hl,(FRAME)
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x4000
 add hl,de
 ld de,#SKY
 ld bc,#8
 ldir
 ld a,(STAGE)
 cp #2
 jr nz,exterior_sky
 call interior_clear
 jp base_scene_ready
exterior_sky:
 call interior_sky
 call steer_sky
 ld hl,#background
 call load15
 ld hl,(SKY)
 ld (CMD),hl
 ld hl,(SKY+2)
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 ld a,#32
 ld b,#17
 call wreg
 ld hl,#CMD
 ld bc,#0x0E9B
 otir
 ld a,#47
 ld b,#17
 call wreg
 ld hl,#SKY+4
 ld bc,#0x049B
 otir
 ld a,#0x30
 ld b,#46
 call wreg
 call waitce
base_scene_ready:
 ld a,(STAGE)
 cp #2
 jr z,no_stars
 call speed_streaks
no_stars:
 call draw_wall
 call make_poses
 ; Stream distinct meshes as required; geometry rendered by Geo3D.
 ld a,#1
 ld (0x6000),a
 ld a,#0x46
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(PAGE)
 out (0x9F),a
 ld hl,#REC
 ld (PTR),hl
 ld a,#6
 ld (COUNT),a
jet_loop:
 ld a,(COUNT)
 ld e,a
 ld d,#0
 ld hl,#REC+512
 or a
 sbc hl,de
 ld a,(hl)
 cp #255
 jr nz,visible_object
 ld hl,(PTR)
 ld de,#24
 add hl,de
 ld (PTR),hl
 jp next_object
visible_object:
 push af
 call loadmodel
 pop af
 or a
 ld hl,#light
 jr nz,material_ready
 ld hl,#ravenlight
material_ready:
 ld a,#0x5A
 out (0x9D),a
 ld bc,#0x069F
 otir
 xor a
 out (0x9D),a
 ld hl,(PTR)
 ld bc,#0x189F
 otir
 ld (PTR),hl
 ld a,#0x48
 out (0x9D),a
 ld a,#3
 out (0x9F),a
geo_wait:
 call fm_poll
 in a,(0x9D)
 and #1
 jr nz,geo_wait
next_object:
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 jp nz,jet_loop
 call game_draw
frame_pace:
 call fm_poll
 in a,(0xE7)
 cp #12
 jr c,frame_pace
 call vblank
 ld a,(PAGE)
 rrca
 rrca
 rrca
 or #31
 ld b,#2
 call wreg
 ld hl,(DONE)
 inc hl
 inc hl
 inc hl
 ld (DONE),hl
 ld a,(PAUSED)
 or a
 jp nz,main
 ld hl,(FRAME)
 inc hl
 inc hl
 inc hl
 inc hl
 ld a,h
 cp #6
 jr c,frame_ok
 ld hl,#0
frame_ok:
 ld (FRAME),hl
 jp main
draw_wall:
 xor a
 ld (0xE7F3),a
draw_wall_pass:
 ld a,(STAGE)
 cp #3
 ret z
 ld hl,(FRAME)
 ld a,h
 srl a
 add a,#56
 ld (0x6000),a
 ld a,h
 and #1
 ld h,a
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x4000
 add hl,de
 ld de,#WALL
 ld bc,#32
 ldir
 call interior_transform
 call steer_wall
 ld a,#0x46
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(PAGE)
 out (0x9F),a
 ld a,#0x5A
 out (0x9D),a
 ld hl,#light
 ld bc,#0x069F
 otir
 ld a,#255
 ld (0xE53F),a
 ; Furthest module first, towards the camera.
 ld a,#4
 ld (WCOUNT),a
wall_far:
 call wall_advance
 ld a,(WCOUNT)
 dec a
 ld (WCOUNT),a
 jr nz,wall_far
 ld a,#5
 ld (WCOUNT),a
wall_loop:
 ld hl,#WALL+31
 srl (hl)
 jr nc,wall_skipped
 call load_wall_district
 xor a
 out (0x9D),a
 ld hl,#WALL
 ld bc,#0x189F
 otir
 ld a,#0x48
 out (0x9D),a
 ld a,#3
 out (0x9F),a
wall_busy:
 call fm_poll
 in a,(0x9D)
 and #1
 jr nz,wall_busy
wall_skipped:
 ld hl,(WALL+18)
 ld de,(WALL+24)
 or a
 sbc hl,de
 ld (WALL+18),hl
 ld hl,(WALL+20)
 ld de,(WALL+26)
 or a
 sbc hl,de
 ld (WALL+20),hl
 ld hl,(WALL+22)
 ld de,(WALL+28)
 or a
 sbc hl,de
 ld (WALL+22),hl
 ld a,(WCOUNT)
 dec a
 ld (WCOUNT),a
 jr nz,wall_loop
 ld a,(STAGE)
 cp #2
 jr nz,wall_finish
 ld a,(0xE7F3)
 or a
 jr nz,wall_finish
 inc a
 ld (0xE7F3),a
 jp draw_wall_pass
wall_finish:
 ld a,#1
 ld (0x6000),a
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0x400E)
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,#0x4020
 ld de,(0x400F)
 call geoblock
 ld a,#255
 ld (MODEL),a
 ret
load_wall_district:
 ld a,(STAGE)
 cp #2
 jp z,interior_bank
 ld a,(WALL+30)
 ld b,a
 ld a,(WCOUNT)
 dec a
 add a,b
 cp #5
 jr c,wall_bank_ready
 sub #5
wall_bank_ready:
 ld hl,#wall_banks
 ld e,a
 ld d,#0
 add hl,de
 ld a,(hl)
wall_bank_selected:
 ld b,a
 ld a,(STAGE)
 cp #2
 jr nz,wall_actual_bank
 ld a,(0xE7F3)
 or a
 jr nz,wall_actual_bank
 ld a,b
 cp #5
 ld b,#38
 jr nz,wall_actual_bank
 ld b,#39
wall_actual_bank:
 ld a,b
 ld a,(0xE53F)
 cp b
 ret z
 ld a,b
 ld (0xE53F),a
 ld (0x6000),a
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0x4000)
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,#0x4006
 ld de,(0x4002)
 call geoblock
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(0x4001)
 out (0x9F),a
 ld a,#0x52
 out (0x9D),a
 ld de,(0x4004)
 call geoblock
 ret
wall_banks:
 .db 55,59,60,61,62
wall_advance:
 ld hl,(WALL+18)
 ld de,(WALL+24)
 add hl,de
 ld (WALL+18),hl
 ld hl,(WALL+20)
 ld de,(WALL+26)
 add hl,de
 ld (WALL+20),hl
 ld hl,(WALL+22)
 ld de,(WALL+28)
 add hl,de
 ld (WALL+22),hl
 ret
draw_lines:
 ld hl,(PTR)
 ld de,#CMD
 ld bc,#11
 ldir
 ld (PTR),hl
 ld a,(PAGE)
 ld (CMD+3),a
 ld a,#36
 ld b,#17
 call wreg
 ld hl,#CMD
 ld bc,#0x0B9B
 otir
 call waitce
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 jr nz,draw_lines
 ret
loadmodel:
 ld b,a
 ld a,(MODEL)
 cp b
 ret z
 ld a,b
 ld (MODEL),a
 add a,a
 ld l,a
 ld h,#0x40
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(hl)
 out (0x9F),a
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,#0x52
 out (0x9D),a
 call geoblock
 ret
wreg:
 out (0x99),a
 ld a,b
 or #0x80
 out (0x99),a
 ret
status2:
 ld a,#2
 ld b,#15
 call wreg
 in a,(0x99)
 ret
waitce:
 call fm_poll
 call status2
 and #1
 jr nz,waitce
 ret
vblank:
 call fm_poll
 call status2
 and #0x40
 jr nz,vblank
vbnext:
 call fm_poll
 call status2
 and #0x40
 jr z,vbnext
 ret
load15:
 ld de,#CMD
 ld bc,#15
 ldir
 ret
send15:
 ld a,#32
 ld b,#17
 call wreg
 ld hl,#CMD
 ld bc,#0x0F9B
 otir
 ret
geoblock:
 ld c,#0x9F
 jr block
vramblock:
 ld c,#0x98
block:
 ld a,d
 or a
 jr z,tail
blockloop:
 ld b,#0
 otir
 dec a
 jr nz,blockloop
tail:
 ld a,e
 or a
 ret z
 ld b,e
 otir
 ret
regs:
 .db 0,6,1,0,2,31,7,0,8,10,9,128,21,0,20,1,51,0,52,0,53,0,54,0,55,255,56,0,57,255,58,3,255
camera:
 .dw 256,128,106,40,256,212
light:
 .dw -5000,10500,-11500
background:
 .dw 0,512,0,14,256,184
 .db 0,0,0x30
hudtop:
 .dw 0,512,0,0,256,14
 .db 0,0,0xD0
hudbottom:
 .dw 0,710,0,198,256,14
 .db 0,0,0xD0
.include "palette.inc"

ravenlight:
 .dw -2900,6090,-6670

shieldbar:
 .dw 0,0,23,202,48,6
 .db 13,0,0xC0

pickup_notes:
 .db 42,56,70

.include "game.inc"

title_screen:
 ld hl,#title_copy
 call load15
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
title_copy:
 .dw 0,0,0,0,256,212
 .db 0,0,0xD0

assets8:
 .db 30,0,31,1,22,4,23,5,24,6,25,7,255

.include "fm.inc"
