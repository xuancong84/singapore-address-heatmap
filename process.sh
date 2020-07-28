#!/usr/bin/env bash

zcat -f singpostcode.json.gz | sed "s:\([&#@]\): \1 :g; s: RD : ROAD :g; s:  *: :g" | python3 -c "
import os, sys, json
trim = lambda t: ' '.join(t.split())
db = json.loads(sys.stdin.read())
db = [{k:((' %s '%trim(v.replace(',', ' '))) if k=='ADDRESS' else trim(v)) for k,v in d.items()} for d in db]
for e in db:
	del e['LONGTITUDE']
	del e['SEARCHVAL']
	e['LATITUDE'] = '%.6f'%float(e['LATITUDE'])
	e['LONGITUDE'] = '%.6f'%float(e['LONGITUDE'])
	e['X'] = '%.5f'%float(e['X'])
	e['Y'] = '%.5f'%float(e['Y'])
print(json.dumps(db, indent=1))
" | sed "s:\"\([0-9]*\.[0-9][0-9]*\)\":\1:g" | gzip > database.json.gz &

zcat -f singpostcode.json.gz | sed "s:\([&#@]\): \1 :g; s: RD : ROAD :g; s:  *: :g" | python3 -c "
import os, sys, json
import pandas as pd
trim = lambda t: ' '.join(t.split())
db = json.loads(sys.stdin.read())
db = [{k:((' %s '%trim(v.replace(',', ' '))) if k=='ADDRESS' else trim(v)) for k,v in d.items()} for d in db]
for e in db:
	del e['LONGTITUDE']
	del e['SEARCHVAL']
	e['LATITUDE'] = '%.6f'%float(e['LATITUDE'])
	e['LONGITUDE'] = '%.6f'%float(e['LONGITUDE'])
	e['X'] = '%.5f'%float(e['X'])
	e['Y'] = '%.5f'%float(e['Y'])
df = pd.DataFrame(db)
df.POSTAL = df.POSTAL.replace('NIL', 0).astype(int)
df.to_csv('database.csv.gz', index=False)
" &

wait
