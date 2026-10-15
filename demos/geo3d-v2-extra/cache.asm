; Geo3D v2 model cache. All addresses/counts are validated by build_v2.py.
; Source geometry remains resident; VFIRST/FFIRST select each cached model.
; Face + UV identity is independent of animated vertex identity.
v2_init:
 ld a,#0x49
 out (0x9D),a
 in a,(0x9F)
 cp #0x20
 jp nz,v2_unsupported
 ld a,#0x6F
 out (0x9D),a
 in a,(0x9F)
 and #0xF0
 cp #0xA0
 jp nz,v2_unsupported
 ld a,#0x6F
 out (0x9D),a
 ld a,#1
 out (0x9F),a
 ld a,#0x68
 out (0x9D),a
 xor a
 ld b,#7
v2_zero_high:
 out (0x9F),a
 djnz v2_zero_high
 ld (0xE518),a
v2_clear_cache:
 ld hl,#0xE540
 ld de,#0xE541
 ld bc,#31
 ld (hl),a
 ldir
 ret
v2_unsupported:
 ld a,#6
 ld b,#7
 call wreg
 jp v2_unsupported
load_geometry:
 ; HL -> descriptor: vertex ID, topology ID, cache byte offset, NV, NF,
 ; LOP, VFIRST, FFIRST, vertex bytes, extended-face bytes, UV bytes.
 ld de,#0xE500
 ld bc,#18
 ldir
 ld (0xE512),hl
 ; A layout change repacks the slots. Invalidate all overlapping ranges.
 ld a,(0xE507)
 and #0xF0
 ld b,a
 ld a,(0xE518)
 cp b
 jr z,v2_layout_ready
 ld a,b
 ld (0xE518),a
 xor a
 call v2_clear_cache
v2_layout_ready:
 ld a,#0x54
 out (0x9D),a
 ld hl,#0xE508
 ld bc,#0x049F
 otir
 ld a,#0x42
 out (0x9D),a
 ld a,(0xE505)
 out (0x9F),a
 xor a
 out (0x9F),a
 ld a,#15
 out (0x9F),a
 ld a,(0xE507)
 and #15
 out (0x9F),a
 ld a,#0x59
 out (0x9D),a
 ld a,(0xE506)
 out (0x9F),a
 ld a,(0xE504)
 ld l,a
 ld h,#0
 ld de,#0xE540
 add hl,de
 ld (0xE514),hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld hl,(0xE500)
 or a
 sbc hl,de
 jr z,v2_vertices_hit
 ld hl,(0xE514)
 ld de,(0xE500)
 ld (hl),e
 inc hl
 ld (hl),d
 ld a,#0x40
 out (0x9D),a
 ld a,(0xE508)
 out (0x9F),a
 ld a,#0x68
 out (0x9D),a
 ld a,(0xE509)
 out (0x9F),a
 ld a,#0x50
 out (0x9D),a
 ld hl,(0xE512)
 ld de,(0xE50C)
 call geoblock
 jr v2_faces
v2_vertices_hit:
 ld hl,(0xE512)
 ld de,(0xE50C)
 add hl,de
v2_faces:
 ld (0xE512),hl
 ld hl,(0xE514)
 inc hl
 inc hl
 ld (0xE514),hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld hl,(0xE502)
 or a
 sbc hl,de
 ret z
 ld hl,(0xE514)
 ld de,(0xE502)
 ld (hl),e
 inc hl
 ld (hl),d
 ld a,#0x58
 out (0x9D),a
 ld a,(0xE50A)
 out (0x9F),a
 ld a,#0x6C
 out (0x9D),a
 ld a,(0xE50B)
 out (0x9F),a
 ld a,#0x52
 out (0x9D),a
 ld hl,(0xE512)
 ld de,(0xE50E)
 call geoblock
 ld a,#0x65
 out (0x9D),a
 ld a,(0xE50A)
 out (0x9F),a
 ld a,#0x6E
 out (0x9D),a
 ld a,(0xE50B)
 out (0x9F),a
 ld a,#0x53
 out (0x9D),a
 ld de,(0xE510)
 ld a,d
 or e
 ret z
 jp geoblock
