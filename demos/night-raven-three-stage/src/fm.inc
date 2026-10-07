; Original provisional three-voice OPLL score, channel 8 impact/launch effects.
FM_CLOCK=0xE53B
FM_STEP=0xE53C
FM_EFFECT=0xE53D
fm_write:
 push bc
 push af
 ld a,b
 out (0x7C),a
 ld b,#32
fm_aw:
 djnz fm_aw
 pop af
 out (0x7D),a
 ld b,#128
fm_dw:
 djnz fm_dw
 pop bc
 ret
fm_init:
 ld a,#34
 ld (0x6000),a
 ld hl,#0x4000
 ld de,#0xE800
 ld bc,#2048
 ldir
 xor a
 ld (0xE7F2),a
 in a,(0xE7)
 ld (0xE7F1),a
 ld a,#1
 ld (0xE7F0),a
 ld b,#0x0E
 xor a
 call fm_write
 ld b,#0x30
 ld a,#0xE3
 call fm_write
 inc b
 ld a,#0x37
 call fm_write
 inc b
 ld a,#0x18
 call fm_write
 ld b,#0x33
 ld a,#0x1C
 call fm_write
 ; Dedicated OPLL rhythm voices, separate from the quiet lead.
 ld b,#0x36
 ld a,#5
 call fm_write
 inc b
 ld a,#0x65
 call fm_write
 inc b
 ld a,#0x77
 call fm_write
 ld b,#0x16
 ld a,#0x20
 call fm_write
 ld b,#0x26
 ld a,#5
 call fm_write
 ld b,#0x17
 ld a,#0x50
 call fm_write
 ld b,#0x27
 ld a,#5
 call fm_write
 ld b,#0x18
 ld a,#0xC0
 call fm_write
 ld b,#0x28
 ld a,#1
 call fm_write
 ld b,#0x0E
 ld a,#0x20
 jp fm_write
fm_poll:
 push af
 ld a,(0xE7F0)
 or a
 jr z,fm_poll_exit
 push bc
 in a,(0xE7)
 ld b,a
 ld a,(0xE7F1)
 cp b
 jr z,fm_poll_same
 ld c,a
 ld a,b
 ld (0xE7F1),a
 sub c
 push de
 push hl
 call fm_tick
 pop hl
 pop de
fm_poll_same:
 pop bc
fm_poll_exit:
 pop af
 ret
fm_tick:
 ld c,a
 ld a,(PAUSED)
 or a
 jr nz,fm_stopped
 ld a,(GS)
 cp #2
 jr z,fm_stopped
 xor a
 ld (0xE7F2),a
 ld a,(FM_CLOCK)
 add a,c
 cp #100
 jr nc,fm_beat
 ld (FM_CLOCK),a
 ret
fm_stopped:
 xor a
 ld (FM_CLOCK),a
 ld a,(0xE7F2)
 or a
 ret nz
 inc a
 ld (0xE7F2),a
 jp fm_silence
fm_beat:
 sub #100
 ld (FM_CLOCK),a
 ld a,(FM_STEP)
 inc a
 ld (FM_STEP),a
 push af
 ld b,#0x0E
 ld a,#0x20
 call fm_write
 pop af
 push af
 and #3
 ld a,#0x21
 jr nz,fm_hat
 ld a,#0x31
fm_hat:
 ld c,a
 pop af
 push af
 and #7
 cp #4
 ld a,c
 jr nz,fm_drum
 ld a,#0x29
fm_drum:
 call fm_write
 pop af
 ld l,a
 ld h,#0
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,#0xE800
 add hl,de
 ld c,#0
fm_voice:
 inc hl
 ld a,(hl)
 dec hl
 cp #255
 jr nz,fm_new_note
 inc hl
 inc hl
 jr fm_voice_next
fm_new_note:
 ld a,c
 add a,#0x20
 ld b,a
 xor a
 call fm_write
 ld a,c
 add a,#0x10
 ld b,a
 ld a,(hl)
 inc hl
 call fm_write
 ld a,c
 add a,#0x20
 ld b,a
 ld a,(hl)
 inc hl
 call fm_write
fm_voice_next:
 inc c
 ld a,c
 cp #4
 jr c,fm_voice
 ret
fm_silence:
 ld b,#0x20
 xor a
 call fm_write
 inc b
 xor a
 call fm_write
 inc b
 xor a
 call fm_write
 inc b
 xor a
 call fm_write
 ld b,#0x0E
 ld a,#0x20
 jp fm_write
