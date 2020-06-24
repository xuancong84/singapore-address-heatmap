
zcat -f singpostcode.json.gz | sed "s:\([&#@]\): \1 :g; s: RD : ROAD :g; s:  *: :g" | python3 -c "
import os, sys, json
trim = lambda t: ' '.join(t.split())
db = json.loads(sys.stdin.read())
db = [{k:trim(v.replace(',', ' ') if k=='ADDRESS' else v) for k,v in d.items()} for d in db]
print(json.dumps(db, indent=1))
" | gzip > database.json.gz

