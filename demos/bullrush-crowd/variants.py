from pathlib import Path
p=Path(__file__).resolve().parent/'out';b=(p/'BULLRUSH.ROM').read_bytes()
for n in range(b[16*16384+271]+1):
 a=bytearray(b)
 for f in range(576):
  off=16*16384+512*f;g=[a[off+272+31*j:off+303+31*j] for j in range(b[16*16384+271])]
  red=[x for x in g if x[29]&128];bl=[x for x in g if not x[29]&128]
  selected=[x for x in g if x[30]<n]
  a[off+271]=n
  for j,x in enumerate(selected):a[off+272+31*j:off+303+31*j]=x
 (p/f'BULLRUSH-{n+2}robots.ROM').write_bytes(a)
