; ORBITAL - Geo3D textured terrain flight demo.
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
 ld bc,#0x800
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
 ; Restore the original bulk loop for R800. Z80 keeps the unrolled loop.
 ld hl,#block
 ld (geoblock+3),hl
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
 ; Scene atlas on VRAM page 2.
 ld a,#4
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x40
 out (0x99),a
 ld a,#4
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#5
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ; Additional HUD atlas in VRAM page 3.
 ld a,#6
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x40
 out (0x99),a
 ld a,#6
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#7
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ; Seven shaded Earth/Moon atlas copies at VRAM Y=1024.
 ld a,#8
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x40
 out (0x99),a
 ld a,#8
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#9
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#10
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#11
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#12
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#13
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#14
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#0x60
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 out (0x9F),a
 ld a,#4
 out (0x9F),a
 ld a,#128
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
 ld hl,(REC+176)
 ld (CMD),hl
 ld hl,(REC+178)
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
 ld hl,#REC+180
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
 ld a,#7
 ld (COUNT),a
object_loop:
 ld a,(COUNT)
 ld e,a
 ld d,#0
 ld hl,#REC+175
 or a
 sbc hl,de
 ld a,(hl)
 cp #255
 jr z,skip_object
 ld (0x6000),a
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
 ld hl,#hudtop
 call load15
 ld hl,(REC+184)
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 ld hl,#hudbottom
 call load15
 ld hl,(REC+186)
 ld (CMD+2),hl
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
frame_pace:
 in a,(0xE7)
 cp #22
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
 ld hl,(FRAME)
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
load_geometry:
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,(0x4000)
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
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
 ld a,#0x65
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,#0x53
 out (0x9D),a
 push hl
 ld a,(0x4001)
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
 ; Geo3D-only bulk upload: 16 OUTI instructions per loop.
 ; Leave VDP transfers and short Geo3D tails at their original timing.
 ld c,#0x9F
 jp geo_fast_body
geo_fast_body:
 ld a,d
 or a
 jr z,geo_fast_tail
geo_fast_page:
 ld b,#0
geo_fast_chunk:
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
 jp nz,geo_fast_chunk
 dec a
 jr nz,geo_fast_page
geo_fast_tail:
 ld a,e
 or a
 ret z
 ld b,e
 otir
 ret
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
 .db 0,6,1,0,2,31,7,0,8,10,9,128,21,0,20,1,51,0,52,0,53,0,54,0,55,255,56,0,57,255,58,7,255
camera:
 .dw 170,128,106,4,256,212
light:
 .dw -6000,7000,-13500
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
