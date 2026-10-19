; Contact is used ONLY for sparkles; never for music or animation progression.
; E490/E491: TTL per instrument, E492: last raw flag, E498: sampled instrument.
spark_init:
 xor a
 ld (0xE490),a
 ld (0xE491),a
 ld (0xE492),a
 ld (0xE494),a
 ld (0xE496),a
 ld (0xE498),a
 ld a,#3
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x70
 out (0x99),a
 ld hl,#spark_patterns
 ld bc,#0x1098
 otir
 xor a
 out (0x99),a
 ld a,#0x78
 out (0x99),a
 ld e,#2
spark_color_pair:
 ld b,#16
 ld a,#9
spark_color_visible:
 out (0x98),a
 djnz spark_color_visible
 ld b,#16
 xor a
spark_color_hidden:
 out (0x98),a
 djnz spark_color_hidden
 dec e
 jr nz,spark_color_pair
 xor a
 out (0x99),a
 ld a,#0x7A
 out (0x99),a
 ld a,#216
 out (0x98),a
 ret
spark_patterns:
 .db 24,60,126,255,255,126,60,24
 .db 255,255,255,255,255,255,0,0
spark_clear:
 xor a
 ld b,#15
 call wreg
 in a,(0x99)
 ret
spark_positions:
 ld a,(REC+236)
 ld (0xE498),a
 ld a,#3
 ld b,#14
 call wreg
 xor a
 out (0x99),a
 ld a,#0x7A
 out (0x99),a
 ld hl,#REC+220
 ld bc,#0x1098
 otir
 ld a,#216
 out (0x98),a
 ; Match the visible mallet head: yellow cat, white rabbit.
 xor a
 out (0x99),a
 ld a,#0x78
 out (0x99),a
 ld a,(0xE498)
 or a
 ld a,#9
 jr z,spark_head_color
 ld a,#15
spark_head_color:
 ld c,a
 ld e,#2
spark_recolor:
 ld a,c
 ld b,#16
spark_recolor_head:
 out (0x98),a
 djnz spark_recolor_head
 xor a
 ld b,#16
spark_recolor_receiver:
 out (0x98),a
 djnz spark_recolor_receiver
 dec e
 jr nz,spark_recolor
 ret
spark_sample:
 call spark_clear
 and #0x20
 ld (0xE492),a
 push af
 ld hl,#0xE490
 ld b,#2
spark_decay:
 ld a,(hl)
 or a
 jr z,spark_decay_next
 dec (hl)
spark_decay_next:
 inc hl
 djnz spark_decay
 pop af
 or a
 ret z
 ld a,(0xE498)
 ld e,a
 ld d,#0
 ld hl,#0xE490
 add hl,de
 ld (hl),#4
 ld hl,#0xE494
 add hl,de
 add hl,de
 inc (hl)
 ret
spark_draw:
 ld a,(0xE490)
 or a
 jr z,spark_rabbit
 ld c,#45
 call spark_tile
spark_rabbit:
 ld a,(0xE491)
 or a
 ret z
 ld c,#163
spark_tile:
 push af
 push bc
 ld hl,#spark_command
 call load15
 pop bc
 pop af
 cp #3
 jr nc,spark_bright
 ld hl,#48
 ld (CMD),hl
spark_bright:
 ld a,c
 ld (CMD+4),a
 ld a,(PAGE)
 ld (CMD+7),a
 call send15
 jp waitce
spark_command:
 .dw 0,1792,0,121,48,32
 .db 0,0,0x98
