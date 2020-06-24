#!/usr/bin/env python3

import os, sys, gzip, json, argparse, re


def Open(fn, mode='r', **kwargs):
	if fn == '-':
		return sys.stdin if mode.startswith('r') else sys.stdout
	return gzip.open(fn, mode, **kwargs) if fn.lower().endswith('.gz') else open(fn, mode, **kwargs)

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

	def search(self, addrname):
		name = addrname.upper().replace(',', ' ')
		name = trim(re.sub('([&#@()])', ' \\1 ', name))
		names = name.split()

		# try to extract BLK number
		try:
			blk_pos = names.index('BLK') if 'BLK' in name else (names.index['BLOCK'] if 'BLOCK' in names else None)
			blk = names[blk_pos+1]
			del names[blk_pos:blk_pos+2]
		except:
			blk = None

		# try to extract names inside ()
		brack_data = []
		try:
			while '(' in names:
				pos1 = names.index('(')
				pos2 = names.index(')', pos1+1)
				if pos2>pos1+1:
					brack_data += [' '.join(names[pos1+1:pos2])]
				del names[pos1:pos2+1]
		except:
			pass

		s_pattn = ' '.join(names)
		res = [i for i in self.db if s_pattn in i['ADDRESS']]

		# confine search by block number
		if blk != None and len(res)>1:
			res1 = [i for i in res if i['BLK_NO']==blk]
			res = res1 if res1 else res

		# confine search by names in brackets
		while brack_data and len(res)>1:
			e = ' %s '%brack_data.pop()
			res1 = [i for i in res if e in ' %s '%(i['ADDRESS'])]
			res = res1 if res1 else res

		return res


if __name__=='__main__':
	parser = argparse.ArgumentParser(usage='$0 <input 1>output 2>progress', description='perform street directory search',
			formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--addr-db', '-d', help='Singapore address database file', type=str, default='database.json.gz')
	parser.add_argument('-optional', help='optional argument')
	#nargs='?': optional positional argument; action='append': multiple instances of the arg; type=; default=
	opt=parser.parse_args()
	globals().update(vars(opt))

	db = AddrDB(addr_db)

	while True:
		try:
			L = input()
			res = db.search(L)
			print(res)
		except:
			break

