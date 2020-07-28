#!/usr/bin/env python3
# Map-highlighter library, requires folium

import folium, re, math
from matplotlib import colors
from collections import *
from dbsearch import *
import pandas as pd
from folium import plugins
from folium_addons.heatmaps import *


def drawElement(draw_data, map_obj):
	# prepare default argument
	add_args = [[re.sub('[A-Z]', lambda t: '_' + t.group().lower(), e[0]), *e[1:]] for e in draw_data['add_args']]
	n_add = len(add_args)
	prev_vargs = {obj[0]: (None if len(obj) == 1 else obj[1]) for obj in add_args}

	# draw main-loop
	func = getattr(folium, draw_data['func'])
	n_fix_args = draw_data['n_fix_args']
	for obj in draw_data['obj_list']:
		vargs = {aa[0]: (obj[k] if (len(obj) > k and obj[k] != None) else (aa[1] if len(aa) > 1 else prev_vargs[aa[0]])) \
		         for j, k, aa in zip(range(n_add), range(n_fix_args, n_fix_args + n_add), add_args)}
		func(*obj[:n_fix_args], **vargs).add_to(map_obj)
		prev_vargs = vargs
	return draw_data


def drawElements(draw_array, map_obj):
	if type(draw_array) == list:
		for e in draw_array:
			try:
				drawElement(e, map_obj)
			except:
				pass
	return draw_array


addr_db = AddrDB('database.json.gz')
nan = float('nan')


def inferLatLon(df):
	df = df.copy()
	def addr2geo(addr):
		try:
			if not math.isnan(addr.latitude) and not math.isnan(addr.longitude):
				return pd.Series([addr.latitude, addr.longitude])
			addrs = addr_db[addr.address]
			assert addrs
			return pd.Series(compute_mean_geo(addrs))
		except:
			return pd.Series([nan, nan])

	if 'count' not in df.columns:
		df['count'] = 1

	if 'latitude' not in df.columns or 'longitude' not in df.columns:
		df['latitude'] = df['longitude'] = nan

	# fill in missing geo-coordinates
	df[['latitude', 'longitude']] = df.apply(addr2geo, axis=1).rename(columns={0: 'latitude', 1: 'longitude'})
	return df.dropna(how='any')


def showCountmaps(obj, map_obj, radius_factor={}, add_args=[], stderr=None):
	# obj = {'red':{'address1':count1, 'address2':count2}, '#00FF00':{...}}
	# <address> can be: a) int => postal code; b) string => address-to-be-searched-for; c) [float,float] => direct [latitude, longitude]
	global addr_db

	draw_array = []
	for color, addr2cnt in (obj.items() if hasattr(obj, 'items') else obj):
		if isinstance(addr2cnt, pd.DataFrame):
			df = inferLatLon(addr2cnt)
			addr2cnt = [[(lat,lon),cnt] for lat,lon,cnt in df[['latitude', 'longitude', 'count']].values.tolist()]

		colorRGB = color if color.startswith('#') else colors.cnames[color]
		geo2cnt = defaultdict(lambda: 0)
		for addr, cnt in (addr2cnt.items() if type(addr2cnt) == dict else addr2cnt):
			if type(addr) in [int, str]:
				addrs = addr_db[addr]
				if not addrs:
					if stderr != None:
						print('Address not found: %s' % addr, file=stderr)
					continue
				geo = compute_mean_geo(addrs)
				geo2cnt[tuple(geo)] += cnt
			elif type(addr) in [list, tuple] and len(addr) == 2:
				geo2cnt[tuple(addr)] += cnt

		# total area of all circles add up to half of Singapore area
		rf = radius_factor.get(color, 1) if isinstance(radius_factor, dict) else radius_factor
		radius_mul = (721500000 / 2 / sum(geo2cnt.values()) / np.pi) ** 0.5 * rf if geo2cnt else 1

		draw_dct = {'func': 'Circle', 'n_fix_args': 1, 'add_args': [['radius'], ['color', colorRGB], *add_args],
		            'obj_list': [[list(geo), (cnt ** 0.5) * radius_mul] for geo, cnt in geo2cnt.items()]}

		draw_array += [draw_dct]

	drawElements(draw_array, map_obj)

	return map_obj


def showHeatmaps(obj, map_obj, freq='1D', smooth=0, min_weight=0.25, add_options={}):
	# INPUT obj = [[color, DataFrame], ...] or {color:DataFrame} or {(color, name):DataFrame}
	# static heatmap:       pd.DataFrame(columns=['address', 'count', duration=pd.Timedelta], index=range())
	# time-stamped heatmap: pd.DataFrame(columns=['address', 'count', duration=pd.Timedelta], index=pd.DatetimeIndex)
	# direct geo-coordinates: pd.DataFrame(columns=['latitude', 'longitude', 'count', pd.Timedelta], index=pd.DatetimeIndex)
	# 'count' and 'duration' column are optional; 0 duration means one period, i.e., '1D' if freq=='D'
	# color: 'red', '#FF0000', None => full color-spectrum heatmap

	def agg_count_set_dt(df_in, dt):
		df = df_in.groupby(['latitude', 'longitude']).sum()
		df['datetime'] = dt
		return df.reset_index().set_index('datetime')

	def norm_count(df, min_weight=0.25):
		try:
			vmax = df['count'].max()
			vdiffi = (1 - min_weight) / vmax
			df['count'] = df['count'].apply(lambda v: v * vdiffi + min_weight)
		except:
			df['count'] = 1
		return df

	def smooth_heatmap(df, freq, N=0):
		# For N>0: count at every time index will spread to adjacent N indices, i.e., N=2, [0,0,1,0,0] => [.25, .5, 1, .5, .25]
		# For N<0: extra abs(N) intermediate time slices will created for linear interpolation, i.e., N=-2, [10,20,30] => [10, 13.33,16.67, 20, 23.33,26.67, 30]
		smooth = abs(N)
		dfs = [df]
		freq = pd.to_timedelta(freq)
		if N > 0:
			for i in range(1, smooth + 1):
				dfC = df.copy()
				dfC['count'] *= 2 ** (-i)
				dfC.index = df.index + freq * i
				dfs += [dfC.copy()]
				dfC.index = df.index - freq * i
				dfs += [dfC]
		elif N < 0:
			for i in range(smooth):
				dfC = df.copy()
				f = (i+1)/(smooth+1)
				dfC['count'] *= f
				dfC.index = df.index + freq * f
				dfs += [dfC.copy()]
				dfC.index = df.index - freq * f
				dfs += [dfC]
			freq /= (smooth+1)
		df = pd.concat(dfs).sort_index()[df.index.min():df.index.max()]
		return df, freq

	isFirstTimedHeatmap = True
	for color, df_raw in (obj.items() if hasattr(obj, 'items') else obj):
		df = df_raw.copy()
		isTimeStamped = isinstance(df.index, pd.DatetimeIndex)

		if 'duration' not in df.columns and isTimeStamped:
			df['duration'] = pd.to_timedelta(0)

		df = inferLatLon(df)

		# extract name and color if color is a tuple
		options = {'min_opacity': 0, 'max_opacity': 1, **add_options}
		color, options['name'] = color if type(color) in [tuple, list] and len(color) == 2 else (color, color)

		# convert color
		try:
			colorRGB = color if color.startswith('#') else colors.cnames[color]
			options['gradient'] = {1: colorRGB}
		except:
			pass

		# create heatmap
		df = df[['latitude', 'longitude', 'count']]
		if isTimeStamped:
			df, freq = smooth_heatmap(df, freq, smooth)
			df = pd.concat([agg_count_set_dt(df1, dt) for dt, df1 in df.groupby(pd.Grouper(freq=freq))])
			df = norm_count(df, min_weight)
			time_list, data_list = list(zip(*[[dt, df1.values.tolist()] for dt, df1 in df.groupby(pd.Grouper(freq=freq))]))
			if isFirstTimedHeatmap:
				isFirstTimedHeatmap = False
				heatmap = HeatMapWithTime(list(data_list), index=[str(i) for i in time_list], **options)
			else:
				heatmap = HeatMapWithTimeAdditional(list(data_list), **options)
		else:
			data_list = norm_count(df, min_weight).values.tolist()
			if 'radius' in options:
				options['radius'] = options['blur'] = options['radius']*2/3
			heatmap = HeatMap(data_list, radius=11, blur=8, **options)

		heatmap.add_to(map_obj)

	folium.LayerControl().add_to(map_obj)

	return map_obj


def addr2geo(arr):
	# INPUT: a list of string (address name) or int (postal code)
	# OUTPUT: a dict of input address to geo-coordinates (latitude, longitude)
	ret = {addr: compute_mean_geo(res) for addr in set(arr) for res in [addr_db[addr]] if res}
	return ret


if __name__ == '__main__':
	my_map = folium.Map([1.34, 103.82], zoom_start=11, control_scale=True, width='50%', height='50%',
	                    tiles="https://maps-{s}.onemap.sg/v3/Default/{z}/{x}/{y}.png",
	                    attr='<a href="http://SLA.gov.sg">Singapore Land Authority</a> &copy; All Rights Reserved!')

	dengue_df = pd.read_csv('../singapore-postal-codes/example/dengue.csv.gz')
	showCountmaps({'blue': dengue_df}, my_map, add_args=[['weight', 1], ['fill', True], ['fillOpacity', '10%']])

	# debug showHeatmaps(...)
	obj = {('red', 'dengue'): pd.DataFrame({'address': ['17 dover crescent', '130017', 'dover crescent blk 18', '130027', '1300270', '6 KIM TIAN ROAD'], 'count': [1,2,3,4,5,6]},
	                                       index=pd.to_datetime(['2020-1-1', '2020-1-1', '2020-1-1', '2020-1-2', '2020-1-3', '2020-1-4'])),
			('#00FF00', 'home'): pd.DataFrame({'address': ['Ghim Moh Link Blk 22', 'Ghim Moh Rd blk 1'], 'count': [5, 10]})}
	showHeatmaps(obj, my_map, smooth=-2)

	# debug showOnMap(...)
	obj = {'red': [[[1.336115, 103.869656], 20],
	               [(1.316022, 103.884446), 7]],
	       '#0000FF': {
		       343443: 1,
		       231132: 1,
		       249715: 8,
		       (1.427745, 103.795128): 2,
		       '6 KIM TIAN ROAD': 5}
	       }

	showOnMap(obj, my_map, add_args=[['weight', 1], ['fill', True], ['fillOpacity', '10%']])
	aa = 5
