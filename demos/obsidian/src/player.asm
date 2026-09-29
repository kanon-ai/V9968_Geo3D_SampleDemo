; OBSIDIAN / original geo3d flyby experiment, 2026
; ASCII16 bank window 4000-7FFF; player executes at E800 in RAM.
; Geometry resident at 8000-E187. No prerecorded raster frames.
.module obsidian
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
 ld bc,#0x0800
 ldir
 jp start
PAGE = 0xE200
FRAME = 0xE202
REC = 0xE300
CMD = 0xE400
ORDER = 0xE410
COUNT = 0xE412
FRAMES_DONE = 0xE420
.org 0xE800
start:
 di
 ld sp,#0xF300
 ; RAM in page 2: all geometry is resident in RAM, not fetched from ROM per frame.
 ; Resolve the actual page-3 RAM slot; RAMAD2 is not reliable during ROM boot.
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
 ld (0x6000),a
 ld (PAGE),a
 ld hl,#0
 ld (FRAME),hl
 ld (FRAMES_DONE),hl
 ; R800 ROM mode on a Turbo R, leave C-BIOS/Z80 untouched.
 ld a,(0x002D)
 cp #3
 jr c,no_r800
 ld a,#0x81
 call 0x0180
 di
no_r800:
 ld de,#0x8000
 ld a,#1
modelcache:
 ld (0x6000),a
 push af
 ld hl,#0x4006
 ld bc,#3121
 ldir
 pop af
 inc a
 cp #9
 jr nz,modelcache
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
 ld bc,#0x209A
 otir
 ; Upload a static HUD/space atlas at VRAM page 2, split in two ROM banks.
 ld a,#4
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x40
 out (0x99),a
 ld a,#9
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#16384
 call vramblock
 ld a,#10
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#10752
 call vramblock
 ; Projection config, fixed focal distance and clipping rectangle.
 ld a,#0x18
 out (0x9D),a
 ld hl,#camera
 ld bc,#0x0C9F
 otir
 ld a,#0x40
 ld b,#1
 call wreg
main:
 ; Each frame record: matrix/translation 24B, light 6B, draw-order 8B,
 ; 24 background stars (x,y,colour) 72B. Remaining bytes reserved.
 ld hl,(FRAME)
 ld a,l
 and #127
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0x4000
 add hl,de
 push hl
 ld hl,(FRAME)
 add hl,hl
 ld a,h
 add a,#11
 ld (0x6000),a
 pop hl
 ld de,#REC
 ld bc,#128
 ldir
 ld a,(PAGE)
 xor #1
 ld (PAGE),a
 ; Copy atlas/background to hidden page.
 ld hl,#background
 call loadcmd
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 ; Perspective stars, behind geometry.
 ld hl,#REC+38
 ld a,#24
 ld (COUNT),a
starloop:
 push hl
 ld hl,#starcmd
 call loadcmd
 pop hl
 ld a,(hl)
 ld (CMD+4),a
 inc hl
 ld a,(hl)
 ld (CMD+6),a
 inc hl
 ld a,(hl)
 ld (CMD+12),a
 inc hl
 ld a,(PAGE)
 ld (CMD+7),a
 push hl
 call send15
 call waitce
 pop hl
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 jr nz,starloop
 ; Transform is common to all spatial sections; hardware performs projection.
 xor a
 out (0x9D),a
 ld hl,#REC
 ld bc,#0x189F
 otir
 ld a,#0x5A
 out (0x9D),a
 ld hl,#REC+24
 ld bc,#0x069F
 otir
 ld a,#0x46
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,(PAGE)
 out (0x9F),a
 ld hl,#REC+30
 ld (ORDER),hl
 ld a,#8
 ld (COUNT),a
modelnext:
 ld hl,(ORDER)
 ld a,(hl)
 inc hl
 ld (ORDER),hl
 dec a
 add a,a
 ld e,a
 ld d,#0
 ld hl,#modelptrs
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 push de
 ; model header: vertex count, face count, vertex byte count, face byte count
 ld a,#0x40
 out (0x9D),a
 xor a
 out (0x9F),a
 out (0x9F),a
 ld a,#225
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,#161
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 pop hl
 ld de,#1350
 call geoblock
 ld a,#0x52
 out (0x9D),a
 ld de,#1771
 call geoblock
 ld a,#0x48
 out (0x9D),a
 ld a,#3
 out (0x9F),a
geowait:
 in a,(0x9D)
 and #1
 jr nz,geowait
 ld a,(COUNT)
 dec a
 ld (COUNT),a
 jp nz,modelnext
 ; Foreground scout: ninth real geo3d submission, banked roll animation.
 ld a,#15
 ld (0x6000),a
 xor a
 out (0x9D),a
 ld hl,#REC+110
 ld bc,#0x129F
 otir
 ld hl,#scoutpos
 ld b,#6
 otir
 ld a,#0x40
 out (0x9D),a
 ld hl,#scoutregs
 ld b,#6
 otir
 ld a,#0x58
 out (0x9D),a
 xor a
 out (0x9F),a
 ld a,#14
 out (0x9F),a
 ld hl,#scoutlight
 ld b,#6
 otir
 ld a,#0x50
 out (0x9D),a
 ld hl,#0x4006
 ld de,#96
 call geoblock
 ld a,#0x52
 out (0x9D),a
 ld de,#154
 call geoblock
 ld a,#0x48
 out (0x9D),a
 ld a,#3
 out (0x9F),a
scoutwait:
 in a,(0x9D)
 and #1
 jr nz,scoutwait
 ; Foreground HUD restores two atlas bands after all polygons.
 ld hl,#hudtop
 call loadcmd
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 ld hl,#hudbottom
 call loadcmd
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 call waitce
 call vblank
 ld a,(PAGE)
 rrca
 rrca
 rrca
 or #0x1F
 ld b,#2
 call wreg
 ld hl,(FRAMES_DONE)
 inc hl
 ld (FRAMES_DONE),hl
 ld hl,(FRAME)
 inc hl
 ld a,h
 and #1
 ld h,a
 ld (FRAME),hl
 jp main
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
loadcmd:
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
 ld a,d
 or a
 jr z,gbtail
gbloop:
 ld b,#0
 otir
 dec a
 jr nz,gbloop
gbtail:
 ld a,e
 or a
 ret z
 ld b,e
 otir
 ret
vramblock:
 ld c,#0x98
vrloop:
 outi
 dec de
 ld a,d
 or e
 jr nz,vrloop
 ret
regs:
 .db 0,6,1,0,2,31,7,0,8,10,9,128,21,0,20,1,255
camera:
 .dw 158,128,106,24,256,212
background:
 .dw 0,512,0,0,256,212
 .db 0,0,0xD0
hudtop:
 .dw 0,512,0,0,256,15
 .db 0,0,0xD0
hudbottom:
 .dw 0,709,0,197,256,15
 .db 0,0,0xD0
starcmd:
 .dw 0,0,0,0,2,1
 .db 0x77,0,0xC0
modelptrs:
 .dw 0x8000,0x8C31,0x9862,0xA493,0xB0C4,0xBCF5,0xC926,0xD557
scoutpos:
 .dw 0,-72,240
scoutregs:
 .db 0,0,16,0,15,0
scoutlight:
 .dw -5000,10000,-11800
.include "palette.inc"
