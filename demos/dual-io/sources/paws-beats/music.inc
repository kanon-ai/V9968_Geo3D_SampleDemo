fmwrite:
 push af
 push bc
 ld a,b
 out (0x7C),a
 ; R800-safe OPLL address/data and successive-write settling times.
 ld a,(0xE49F)
 or a
 ld b,#32
 jr nz,fm_address_wait
 ld b,#3
fm_address_wait:
 djnz fm_address_wait
 pop bc
 pop af
 out (0x7D),a
 push bc
 ld a,(0xE49F)
 or a
 ld b,#128
 jr nz,fmdelay
 ld b,#10
fmdelay:
 djnz fmdelay
 pop bc
 ret
music_init:
 ld hl,#wood_patch
 ld b,#0
 ld c,#8
wood_init:
 ld a,(hl)
 inc hl
 call fmwrite
 inc b
 dec c
 jr nz,wood_init
 ld hl,#rhythm_setup
 ld c,#11
rhythm_init:
 ld b,(hl)
 inc hl
 ld a,(hl)
 inc hl
 call fmwrite
 dec c
 jr nz,rhythm_init
 ret
music_tick:
 ld a,(REC+219)
 or a
 jr nz,music_beat
 ; Short mallet decay, not a held wind-instrument note.
 ld a,(FRAME)
 and #7
 cp #3
 ret nz
 ld a,(REC+209)
 and #0xEF
 ld b,#0x20
 call fmwrite
 ld a,#0x20
 ld b,#0x0E
 jp fmwrite
music_beat:
 ld a,#0x20
 ld b,#0x0E
 call fmwrite
 ld hl,#REC+208
 ld e,#0
music_channel:
 ld a,e
 add a,#0x20
 ld b,a
 xor a
 call fmwrite
 ld a,e
 add a,#0x10
 ld b,a
 ld a,(hl)
 inc hl
 call fmwrite
 ld a,e
 add a,#0x20
 ld b,a
 ld a,(hl)
 inc hl
 call fmwrite
 inc e
 ld a,e
 cp #4
 jr c,music_channel
 ld a,(REC+216)
 ld b,#0x0E
 jp fmwrite
; User patch based on a percussive FM envelope: no vibrato or tremolo.
wood_patch:
 .db 0x17,0x01,0x20,0x07,0xF5,0xF3,0x24,0x24
rhythm_setup:
 .db 0x30,0x00, 0x31,0x0F, 0x32,0x0F, 0x33,0x0F
 .db 0x17,0x50, 0x27,0x05, 0x18,0xC0, 0x28,0x01
 .db 0x37,0xF5, 0x38,0x4F, 0x0E,0x20
