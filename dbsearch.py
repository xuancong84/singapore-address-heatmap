#!/usr/bin/env python3

import os, sys, gzip, json, argparse, re
import numpy as np
from collections import *


def Open(fn, mode='r', **kwargs):
	if fn == '-':
		return sys.stdin if mode.startswith('r') else sys.stdout
	return gzip.open(fn, mode, **kwargs) if fn.lower().endswith('.gz') else open(fn, mode, **kwargs)


def isPostal(s):
	try:
		ii = int(s)
		assert ii >= 0 and ii < 1000000
		return True
	except:
		return False


trim = lambda s: ' '.join(s.split())


class AddrDB:
	def __init__(self, fn_or_fp=None):
		if fn_or_fp == None:
			txt = '[]'
		elif type(fn_or_fp) == str:
			txt = Open(fn_or_fp, 'rt').read()
		else:
			txt = fn_or_fp.read()
			if type(txt) != str:
				txt = txt.decode('utf8', 'ignore')
		self.db = json.loads(txt)
		self.addr_lst = [i['ADDRESS'] for i in self.db]
		self.abbr_dct = {'RD': 'ROAD', 'LK': 'LINK', 'LN': 'LANE', 'PK': 'PARK', 'AVE': 'AVENUE', 'DR': 'DRIVE', 'ST': 'STREET'}
		self.optional = ['ROAD', 'LINK', 'LANE', 'STREET', 'AVENUE', 'DRIVE']
		self.build_postal_db()

	def __getitem__(self, item):
		return self.postal_db.get(int(item), []) if isPostal(item) else self.search(item)

	def build_postal_db(self):
		self.postal_db = defaultdict(lambda: [])
		for e in self.db:
			if isPostal(e['POSTAL']):
				self.postal_db[int(e['POSTAL'])] += [e]
		return self.postal_db

	def search(self, addrname):
		res = self.search_full(addrname)
		if res: return res
		res = self.search_full(addrname, self.abbr_dct)
		if res: return res
		return self.search_full(addrname, self.abbr_dct, self.optional)

	def search_full(self, addrname, abbr={}, opt=[]):
		name = addrname.upper().replace(',', ' ')
		name = trim(re.sub('([&#@()])', ' \\1 ', name))
		for k, v in abbr.items():
			name = name.replace(' %s ' % k, ' %s ' % v)
			name = re.sub(' %s$' % k, ' %s' % v, name)
		for k in opt:
			name = name.replace(' %s ' % k, ' ')
			name = re.sub(' %s$' % k, '', name)
		names = name.split()

		# try to extract BLK number
		try:
			blk_pos = names.index('BLK') if 'BLK' in name else (names.index['BLOCK'] if 'BLOCK' in names else None)
			blk = names[blk_pos + 1]
			del names[blk_pos:blk_pos + 2]
		except:
			blk = None

		# try to extract names inside ()
		brack_data = []
		try:
			while '(' in names:
				pos1 = names.index('(')
				pos2 = names.index(')', pos1 + 1)
				if pos2 > pos1 + 1:
					brack_data += [' '.join(names[pos1 + 1:pos2])]
				del names[pos1:pos2 + 1]
		except:
			names = [s for s in names if s not in ['(', ')']]

		s_pattn = ' ' + ' '.join(names) + ' '
		res = [self.db[i] for i, s in enumerate(self.addr_lst) if s_pattn in s]

		# confine search by block number
		if blk != None and len(res) > 1:
			res1 = [i for i in res if i['BLK_NO'] == blk]
			res = res1 if res1 else res

		# confine search by names in brackets
		while brack_data and len(res) > 1:
			e = ' %s ' % brack_data.pop()
			res1 = [i for i in res if e in i['ADDRESS']]
			res = res1 if res1 else res

		return res


def compute_mean_geo(res):
	mean_lat = np.mean([e['LATITUDE'] for e in res])
	mean_lon = np.mean([e['LONGITUDE'] for e in res])
	return [mean_lat, mean_lon]


if __name__ == '__main__':
	parser = argparse.ArgumentParser(usage='$0 <input 1>output 2>progress', description='perform street directory search',
	                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--addr-db', '-d', help='Singapore address database file', type=str, default='database.json.gz')
	parser.add_argument('--single-line', '-s', help='output single-line JSON format')
	# nargs='?': optional positional argument; action='append': multiple instances of the arg; type=; default=
	opt = parser.parse_args()
	globals().update(vars(opt))

	db = AddrDB(addr_db)

	while True:
		try:
			L = input()
			res = db[L] if L else []
			if single_line:
				print(res)
			else:
				print(json.dumps(res, indent=1))
				print(flush=True)
		except:
			break
