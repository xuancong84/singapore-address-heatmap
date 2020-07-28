#!/usr/bin/env python3

import os, sys, gzip, json, argparse, re
import numpy as np
import pandas as pd
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
	db_cols = ['ADDRESS', 'BLK_NO', 'BUILDING', 'LATITUDE', 'LONGITUDE', 'POSTAL', 'ROAD_NAME', 'X', 'Y']
	def __init__(self, fn_or_df = None):
		self.db = pd.read_csv(fn_or_df) if type(fn_or_df)==str else fn_or_df[self.db_cols]
		self.addr_lst = self.db.ADDRESS.to_list()
		self.abbr_dct = {'RD': 'ROAD', 'LK': 'LINK', 'LN': 'LANE', 'PK': 'PARK', 'AVE': 'AVENUE', 'DR': 'DRIVE', 'ST': 'STREET'}
		self.optional = ['ROAD', 'LINK', 'LANE', 'STREET', 'AVENUE', 'DRIVE']

	def __getitem__(self, item):
		return self.db[self.db.POSTAL == int(item)] if isPostal(item) else self.search(item)

	def search(self, addrname):
		res = self.search_full(addrname)
		if not res.empty: return res
		res = self.search_full(addrname, self.abbr_dct)
		if not res.empty: return res
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
		res = self.db.iloc[[ii for ii, s in enumerate(self.addr_lst) if s_pattn in s], :]

		# confine search by block number
		if blk != None and len(res.index) > 1:
			res1 = res[res.BLK_NO == blk]
			res = res if res1.empty else res1

		# confine search by names in brackets
		while brack_data and len(res.index) > 1:
			e = ' %s ' % brack_data.pop()
			res1 = res[res.ADDRESS.str.contains(e)]
			res = res if res1.empty else res1

		return res.copy()


def compute_mean_geo(res):
	try:
		return [res.LATITUDE.mean(), res.LONGITUDE.mean()]
	except:
		return [float('nan'), float('nan')]


if __name__ == '__main__':
	parser = argparse.ArgumentParser(usage='$0 <input 1>output 2>progress', description='perform street directory search',
	                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--addr-db', '-d', help='Singapore address database file', type=str, default='database.csv.gz')
	parser.add_argument('--single-line', '-s', help='output single-line JSON format')
	# nargs='?': optional positional argument; action='append': multiple instances of the arg; type=; default=
	opt = parser.parse_args()
	globals().update(vars(opt))

	db = AddrDB(addr_db)

	while True:
		try:
			L = input()
		except:
			break

		res = db[L] if L else []
		if single_line:
			print(repr(res.to_csv(index=False)), flush=True)
		else:
			print(res, flush=True)
