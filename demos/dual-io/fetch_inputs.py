from pathlib import Path
import json,hashlib,urllib.request
P=Path(__file__).resolve().parent
for s in json.loads((P/'manifest.json').read_text()):
 p=P/'inputs'/s['id']/s['asset'];p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():data=p.read_bytes()
 else:
  with urllib.request.urlopen(s['url']) as r:data=r.read()
 assert hashlib.sha256(data).hexdigest()==s['sha256'],s['id']
 if not p.exists():p.write_bytes(data)
 print(s['id'],'verified')
