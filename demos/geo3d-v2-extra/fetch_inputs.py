"""Download only the hash-pinned, already-public baseline demo ROMs."""
from pathlib import Path
import json,hashlib,urllib.request
P=Path(__file__).resolve().parent
for spec in json.loads((P/'manifest.json').read_text()):
 target=P/'inputs'/spec['name'];target.parent.mkdir(exist_ok=True)
 if target.exists():data=target.read_bytes()
 else:
  with urllib.request.urlopen(spec['url'],timeout=120) as response:data=response.read()
 assert hashlib.sha256(data).hexdigest()==spec['sha256'],spec['name']+' baseline hash mismatch'
 if not target.exists():target.write_bytes(data)
 print(spec['demo'],'verified')
