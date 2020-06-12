#!/usr/bin/env python

import os, argparse, sys, requests, tqdm, time, json, gzip, random


def pcode_to_data(pcode):
	page = 1
	results = []
	retry_cnt = 0
	while True:
		try:
			response = requests.get('https://developers.onemap.sg/commonapi/search?searchVal=%s&returnGeom=Y&getAddrDetails=Y&pageNum=%d'%(pcode, page)).json()
			results = results + response['results']
			if response['totalNumPages'] > page:
				page = page + 1
			else:
				break
		except:
			if retry_cnt>10:
				print('Fetching %s failed for too many times. Skipping ...'%pcode, file=sys.stderr, flush=True)
				break
			else:
				retry_cnt += 1
				print('Fetching %s failed for %d times. Retrying in 5-10 sec ...'%(pcode, retry_cnt), file=sys.stderr, flush=True)
				time.sleep(5+5*random.random())
				continue

	return results


def Open(fn, mode='r', **kwargs):
	if fn == '-':
		return sys.stdin if mode.startswith('r') else sys.stdout
	return gzip.open(fn, mode, **kwargs) if fn.lower().endswith('.gz') else open(fn, mode, **kwargs)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(usage='$0 [options] 1>output 2>progress', description='Scan and save Singapore postal codes',
	                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--mincode', '-a', help='minimum of the scan range', type=int, default=0)
	parser.add_argument('--maxcode', '-b', help='maximum of the scan range', type=int, default=999999)
	parser.add_argument('--output', '-o', help='output file, "-" for STDOUT', default='singpostcode.json.gz')
	# nargs='?': optional positional argument; action='append': multiple instances of the arg; type=; default=
	opt = parser.parse_args()
	globals().update(vars(opt))

	all_buildings = []
	with tqdm.tqdm(range(mincode, maxcode+1), ncols=120, desc='ScanPostalCode', file=sys.stderr) as tbar:
		for pcode in tbar:
			all_buildings += pcode_to_data('%06d' % pcode)
			if pcode % 1000 == 0:
				tbar.set_postfix(nonempty=len(all_buildings))

	print(json.dumps(all_buildings, indent=2, sort_keys=True), file=Open(output, 'wt'))
