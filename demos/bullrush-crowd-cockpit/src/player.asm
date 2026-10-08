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
 ld de,#0xE800
 ld bc,#0xA00
 ldir
 jp start
VIEW = 0xE444
VIEWKEY = 0xE445
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
TEX = 0xE440
KEYOLD = 0xE441
TOPOLOGY = 0xE442
GEOMHDR = 0xE480
GEOMDATA = 0xE486
SKY = 0xE430
WALL = 0xE450
WCOUNT = 0xE470
.org 0xE800
start:
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
 ld (VIEW),a
 ld (VIEWKEY),a
 ld (KEYOLD),a
 ld (PAGE),a
 ld hl,#0
 ld (FRAME),hl
 ld (DONE),hl
 ld a,#1
 ld (TEX),a
 ld a,#55
 ld (CROWD_COLOR),a
 xor a
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
 ld bc,#0x009A
 otir
 ld b,#0
 otir
 ld b,#0
 otir
 ld hl,#asset_blocks
asset_loop:
 ld a,(hl)
 inc hl
 cp #255
 jr z,assets_ready
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
 jr asset_loop
assets_ready:
 ld a,#0x60
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,#112
 out (0x9F),a
 ld a,#3
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x18
 out (0x9D),a
 ld hl,#camera
 ld bc,#0x0C9F
 otir
 ld a,#0x40
 ld b,#1
 call wreg
main:
 call view_key
 call texture_key
 xor a
 out (0xE6),a
 ld hl,(FRAME)
 ld a,l
 and #31
 add a,a
 add a,#0x40
 ld h,a
 ld l,#0
 push hl
 ld hl,(FRAME)
 add hl,hl
 add hl,hl
 add hl,hl
 ld a,h
 ld e,a
 ld a,(VIEW)
 or a
 ld a,e
 jr z,chase_record
 add a,#48
chase_record:
 add a,#16
 ld (0x6000),a
 pop hl
 ld de,#REC
 ld bc,#512
 ldir
 ld a,(PAGE)
 xor #1
 ld (PAGE),a
 ld hl,#background
 call load15
 ld hl,(REC+250)
 ld (CMD),hl
 ld hl,(REC+252)
 ld a,(TEX)
 or a
 jr z,flat_sky
 ld de,#184
 add hl,de
flat_sky:
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
 ld hl,#REC+254
 ld bc,#0x049B
 otir
 ld a,#0x30
 ld b,#46
 call wreg
 call waitce
 ld a,#0x46
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(PAGE)
 out (0x9F),a
 ld hl,#REC
 ld (PTR),hl
 ld a,#10
 ld (COUNT),a
object_loop:
 ld a,(COUNT)
 cp #6
 call z,crowd_pass
 ld a,(COUNT)
 cp #3
 call z,foreground_pass
 ld hl,#0x4000
 ld (MODEL_PTR),hl
 ld a,(COUNT)
 ld e,a
 ld d,#0
 ld hl,#REC+250
 or a
 sbc hl,de
 ld a,(hl)
 cp #255
 jr z,skip_object
 ld (0x6000),a
 call load_or_reuse_geometry
 xor a
 out (0x9D),a
 ld hl,(PTR)
 ld bc,#0x189F
 otir
 ld (PTR),hl
 ld a,#0x48
 out (0x9D),a
 ld a,(TEX)
 add a,a
 add a,a
 or #3
 out (0x9F),a
geo_wait:
 in a,(0x9D)
 and #1
 jr nz,geo_wait
 jr next_object
skip_object:
 ld hl,(PTR)
 ld de,#24
 add hl,de
 ld (PTR),hl
next_object:
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 jr nz,object_loop
 ld hl,#hudtop
 call load15
 ld hl,(REC+258)
 ld a,(TEX)
 or a
 jr nz,hud_texture_ready
 ld hl,#212
hud_texture_ready:
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 ld hl,#hudbottom
 call load15
 ld hl,(REC+260)
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 call cockpit_overlay
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
 ld (DONE),hl
 ld hl,(FRAME)
 inc hl
 ; Advance the route faster on straights; preserve all pivot/turn samples.
 ld hl,(REC+260)
 ld de,#482
 or a
 sbc hl,de
 ld hl,(FRAME)
 inc hl
 jr nc,route_step_ready
 inc hl
route_step_ready:
 ld de,#576
 or a
 sbc hl,de
 add hl,de
 jr c,frame_ok
reset_frame:
 ld a,(VIEW)
 xor #1
 ld (VIEW),a
 ld hl,#0
frame_ok:
 ld (FRAME),hl
 jp main
load_or_reuse_geometry:
 ; Identical left/right wheel geometry can remain resident for the second wheel.
 ld a,(COUNT)
 cp #5
 jr z,reuse_enemy_wheel
 cp #2
 jp nz,load_geometry
 ld a,(REC+247)
 jr reuse_check
reuse_enemy_wheel:
 ld a,(REC+244)
reuse_check:
 cp #255
 ret nz
 jp load_geometry
load_geometry:
 ld a,(COUNT)
 cp #1
 jp z,load_articulated_body
 cp #4
 jp z,load_articulated_body
 ld hl,(MODEL_PTR)
 ld de,#GEOMHDR
 ld bc,#6
 ldir
 ld (GEOMDATA),hl
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(GEOMHDR)
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,(GEOMDATA)
 ld de,(GEOMHDR+2)
 call geoblock
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(GEOMHDR+1)
 out (0x9F),a
 ld a,#0x52
 out (0x9D),a
 ld de,(GEOMHDR+4)
 call geoblock
 jp load_uv
load_articulated_body:
 ; Bank 1 holds topology; per-frame compact vertex coordinates live in 28+.
 ld a,(COUNT)
 cp #4
 ld a,#1
 jr nz,topology_ready
 ld a,(CROWD_COLOR)
topology_ready:
 ld (TOPOLOGY),a
 ld (0x6000),a
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0x4000)
 ld (0xE438),a
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld a,(COUNT)
 cp #4
 jr z,rival_vertices
 ld hl,(REC+262)
 ld a,(REC+264)
 jr vertex_bank_ready
rival_vertices:
 ld hl,(REC+265)
 ld a,(REC+267)
vertex_bank_ready:
 ld (0x6000),a
 ld a,(0xE438)
 ld b,a
body_vertex_loop:
 ld a,(hl)
 inc hl
 xor #0x80
 out (0x9F),a
 rlca
 sbc a,a
 out (0x9F),a
 ld a,(hl)
 inc hl
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,(hl)
 inc hl
 xor #0x80
 out (0x9F),a
 rlca
 sbc a,a
 out (0x9F),a
 djnz body_vertex_loop
 ld a,(TOPOLOGY)
 ld (0x6000),a
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(0x4001)
 out (0x9F),a
 ld a,#0x52
 out (0x9D),a
 ld hl,#0x4006
 ld de,(0x4002)
 add hl,de
 ld de,(0x4004)
 call geoblock
load_uv:
 ; Only the four city slots use texture coordinates. Armor/wheels are flat.
 ld a,(COUNT)
 cp #7
 ret c
 ld a,(TEX)
 or a
 ret z
 ld a,#0x65
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,#0x53
 out (0x9D),a
 push hl
 ld a,(GEOMHDR+1)
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 ex de,hl
 pop hl
 jp geoblock
texture_key:
 in a,(0xAA)
 ld d,a
 and #0xF0
 or #5
 out (0xAA),a
 in a,(0xA9)
 cpl
 and #2
 ld e,a
 ld a,d
 out (0xAA),a
 ld a,(KEYOLD)
 ld d,a
 ld a,e
 ld (KEYOLD),a
 or a
 ret z
 ld a,d
 or a
 ret nz
 ld a,(TEX)
 xor #1
 ld (TEX),a
 ret
CROWD_COLOR = 0xE490
CROWD_LEFT = 0xE491
CROWD_DATA = 0xE492
CROWD_SAVE = 0xE494
CROWD_META = 0xE496
CROWD_BACKUP = 0xE498
crowd_pass:
 ld hl,(PTR)
 ld (CROWD_SAVE),hl
 ld hl,#REC+265
 ld de,#CROWD_BACKUP
 ld bc,#6
 ldir
 ld a,(REC+271)
 ld (CROWD_LEFT),a
 ld hl,#REC+272
 ld (CROWD_DATA),hl
crowd_next:
 ld a,(CROWD_LEFT)
 or a
 jp z,crowd_done
 ld hl,(CROWD_DATA)
 ld de,#29
 add hl,de
 ld a,(hl)
 ld (CROWD_META),a
 and #127
 cp #127
 jp z,crowd_skip
 or a
 jr nz,crowd_cover_ready
 ld a,#255
crowd_cover_ready:
 ld (REC+270),a
 dec hl
 ld d,(hl)
 dec hl
 ld e,(hl)
 ld (REC+268),de
 dec hl
 ld a,(hl)
 ld (REC+267),a
 dec hl
 ld d,(hl)
 dec hl
 ld e,(hl)
 ld (REC+265),de
 ld a,(CROWD_META)
 and #128
 ld a,#55
 jr z,crowd_color_ready
 ld a,#63
crowd_color_ready:
 ld (CROWD_COLOR),a
 ld hl,(CROWD_DATA)
 ld (PTR),hl
 ld a,#4
 ld (COUNT),a
crowd_object:
 ld a,(COUNT)
 sub #4
 ld a,#3
 jr z,crowd_bank_ready
 ld a,(COUNT)
 cp #6
 ld a,#2
 jr z,crowd_bank_ready
 ld a,#3
crowd_bank_ready:
 ld (0x6000),a
 ld hl,#0x4000
 ld (MODEL_PTR),hl
 call load_geometry
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
crowd_wait:
 in a,(0x9D)
 and #1
 jr nz,crowd_wait
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 cp #3
 jr nz,crowd_object
 call foreground_pass
crowd_skip:
 ld hl,(CROWD_DATA)
 ld de,#31
 add hl,de
 ld (CROWD_DATA),hl
 ld hl,#CROWD_LEFT
 dec (hl)
 jp crowd_next
crowd_done:
 ld hl,#CROWD_BACKUP
 ld de,#REC+265
 ld bc,#6
 ldir
 ld hl,(CROWD_SAVE)
 ld (PTR),hl
 ld a,#55
 ld (CROWD_COLOR),a
 ld a,#6
 ld (COUNT),a
 ret
foreground_pass:
 ld a,(REC+270)
 cp #255
 ret z
 ld (0x6000),a
 ld hl,(REC+268)
 ld (MODEL_PTR),hl
 ld a,#10
 ld (COUNT),a
 call load_geometry
 xor a
 out (0x9D),a
 ld hl,#identity_pose
 ld bc,#0x189F
 otir
 ld a,#0x48
 out (0x9D),a
 ld a,(TEX)
 add a,a
 add a,a
 or #3
 out (0x9F),a
foreground_wait:
 in a,(0x9D)
 and #1
 jr nz,foreground_wait
 ld a,#3
 ld (COUNT),a
 ret
view_key:
 in a,(0xAA)
 ld d,a
 and #0xF0
 or #3
 out (0xAA),a
 in a,(0xA9)
 cpl
 and #1
 ld e,a
 ld a,d
 out (0xAA),a
 ld a,(VIEWKEY)
 ld d,a
 ld a,e
 ld (VIEWKEY),a
 or a
 ret z
 ld a,d
 or a
 ret nz
 ld a,(VIEW)
 xor #1
 ld (VIEW),a
 ret
cockpit_overlay:
 ld a,(VIEW)
 or a
 ret z
 ld hl,#cockpit_rects
 ld a,#10
cock_rect_loop:
 push af
 push hl
 call load15
 ld a,(PAGE)
 ld b,a
 ld a,(CMD+7)
 add a,b
 ld (CMD+7),a
 call send15
 call waitce
 pop hl
 ld de,#15
 add hl,de
 pop af
 dec a
 jr nz,cock_rect_loop
 ret
cockpit_rects:
 .dw 0,0,0,14,5,184
 .db 2,0,0xC0
 .dw 0,0,251,14,5,184
 .db 2,0,0xC0
 .dw 0,0,5,179,246,19
 .db 1,0,0xC0
 .dw 0,0,5,179,246,2
 .db 4,0,0xC0
 .dw 0,0,17,185,52,7
 .db 11,0,0xC0
 .dw 0,0,20,187,35,3
 .db 13,0,0xC0
 .dw 0,0,188,185,48,7
 .db 2,0,0xC0
 .dw 0,0,191,187,29,3
 .db 8,0,0xC0
 .dw 0,0,122,105,12,1
 .db 13,0,0xC0
 .dw 0,0,127,100,1,11
 .db 13,0,0xC0
identity_pose:
 .dw 16384,0,0,0,16384,0,0,0,16384,0,0,0
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
 call status2
 and #1
 jr nz,waitce
 ret
vblank:
 call status2
 and #0x40
 jr nz,vblank
vbnext:
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
asset_blocks:
 .db 4,3,5,7,6,8,7,9,52,10,53,11,54,12,56,13,57,14,58,15,255
regs:
 .db 0,14,1,0,2,31,7,0,8,10,9,128,21,0,20,17,51,0,52,0,53,0,54,0,55,255,56,0,57,255,58,3,255
camera:
 .dw 170,128,106,4,256,212
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

