; CAT ASCENT - Geo3D textured terrain flight demo.
.module petconcert
.area ROM (ABS)
.org 0x4000
.ascii "AB"
.dw boot,0,0,0
.ds 6
boot:
 di
 ld sp,#0xF300
 ld hl,#0x4100
 ld de,#0xD000
 ld bc,#0x1000
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
.org 0xD000
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
 xor a
 ld (0xE49F),a
 ld a,(0x002D)
 cp #3
 jr c,cpu_ready
 ld a,#0x81
 push af
 call 0x0180
 pop af
 and #1
 ld (0xE49F),a
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
 xor a
 out (0x9F),a
 ld a,#3
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x5A
 out (0x9D),a
 ld hl,#light
 ld bc,#0x069F
 otir
 ld a,#0x18
 out (0x9D),a
 ld hl,#camera
 ld bc,#0x0C9F
 otir
 ld a,#0x40
 ld b,#1
 call wreg
main:
 xor a
 out (0xE6),a
 ld hl,(FRAME)
 ld a,l
 and #63
 add a,#0x40
 ld h,a
 ld l,#0
 push hl
 ld hl,(FRAME)
 add hl,hl
 add hl,hl
 ld a,h
 add a,#40
 ld (0x6000),a
 pop hl
 ld de,#REC
 ld bc,#256
 ldir
 ld a,(PAGE)
 xor #1
 ld (PAGE),a
 ld hl,#background
 call load15
 ld hl,(REC+200)
 ld (CMD),hl
 ex de,hl
 ld hl,#256
 or a
 sbc hl,de
 ld (CMD+8),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 ld hl,(REC+200)
 ld a,h
 or l
 jr z,background_complete
 ld (CMD+8),hl
 ex de,hl
 ld hl,#256
 or a
 sbc hl,de
 ld (CMD+4),hl
 ld hl,#0
 ld (CMD),hl
 call send15
 call waitce
background_complete:
 ld a,#0x46
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(PAGE)
 out (0x9F),a
 ld hl,#REC
 ld (PTR),hl
 ld a,#8
 ld (COUNT),a
object_loop:
 ld a,(COUNT)
 ld e,a
 ld d,#0
 ld hl,#REC+200
 or a
 sbc hl,de
 ld a,(hl)
 cp #255
 jr z,skip_object
 ld (0x6000),a
 ld a,#8
 ld hl,#COUNT
 sub (hl)
 add a,a
 ld e,a
 ld d,#0
 ld hl,#REC+202
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 call load_geometry
 xor a
 out (0x9D),a
 ld hl,(PTR)
 ld bc,#0x189F
 otir
 ld (PTR),hl
 ld a,#0x48
 out (0x9D),a
 ld a,#7
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
 call vblank
no_extra_hold:
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
 push hl
 ld de,#900
 or a
 sbc hl,de
 pop hl
 jr c,frame_ok
 ld hl,#0
frame_ok:
 ld (FRAME),hl
 jp main
load_geometry:
 ld de,#0xE4A0
 ld bc,#6
 ldir
 ld (0xE4A6),hl
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0xE4A0)
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,(0xE4A6)
 ld de,(0xE4A2)
 call geoblock
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(0xE4A1)
 out (0x9F),a
 ld a,#0x52
 out (0x9D),a
 ld de,(0xE4A4)
 call geoblock
 ld a,#0x65
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,#0x53
 out (0x9D),a
 push hl
 ld a,(0xE4A1)
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 ex de,hl
 pop hl
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
 ld a,(0xE49F)
 or a
 jp nz,block
 ld a,d
 or a
 jp z,tail
z80_geoblock:
 ld b,#0
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 outi
 dec a
 jp nz,z80_geoblock
 jp tail
vramblock:
 ld c,#0x98
block:
 ld a,d
 or a
 jp z,tail
blockloop:
 ld b,#0
 otir
 dec a
 jp nz,blockloop
tail:
 ld a,e
 or a
 ret z
 ld b,e
 otir
 ret
reload_sky:
 ld a,(hl)
 cp #24
 ret z
 ld (0x6000),a
 inc hl
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
 jr reload_sky
cache_cmd:
 .dw 0,0,0,512,256,212
 .db 0,0,0xD0
asset_blocks:
 .db 4,8,5,9,6,10,7,11,24,12,25,13,26,14,27,15,255
regs:
 .db 0,14,1,0,2,31,7,0,8,10,9,128,21,0,20,17,51,0,52,0,53,0,54,0,55,255,56,0,57,255,58,3,255
camera:
 .dw 1400,128,106,4,256,212
light:
 .dw -6500,8200,-12600
background:
 .dw 0,512,0,0,256,212
 .db 0,0,0xD0
.include "palette.inc"
