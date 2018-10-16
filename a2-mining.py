#!/usr/bin/env python
#
# This code implements the segment mining in Entropy/IP
#   @1 finds frequency outliers (like constants, enums, etc.)
#   @2 finds highly dense ranges of values (like close /32 prefixes)
#   @3 finds uniformly distributed ranges of values (like counters)
#   @4 prints what didn't get into @1-@3
#
# Note that not every piece of the code was mentioned in the paper, as the
# description would be too detailed - this is a heuristics algorithm.
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# Author: Pawel Foremski <pjf@akamai.com>
# Mind the different terminology vs. the paper; excuse the code quality.
# Runs in python2. Requires numpy and scikit-learn.
#

import sys
from collections import defaultdict
import argparse
import math
import numpy as np
from sklearn.cluster import DBSCAN

# segment labels
SL = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", \
      "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

# parse arguments ASAP
p = argparse.ArgumentParser(description='Entropy/IP: segment mining')
p.add_argument('ips', help='file with IPv6 addresses in full hex form')
p.add_argument('segments', help='file with segments (output of a1-segments.py)')
p.add_argument('--segment', help='alternative segment definition')
args = p.parse_args()

###################################### helper functions

def read_segment(segment):
	d = segment.split('-')
	return [{"start":int(d[0]), "stop":int(d[1])}]

def read_segments(src):
	segments = []
	for line in src:
		if line[0:10] != "# segment\t": continue
		d = line[0:-1].split('\t')
		row = {"start":int(d[2]), "stop":int(d[3])}
		segments.append(row)
	return segments

def read_ips(src, segments):
	db = []
	N = 0

	for segment in segments:
		cl = segment.copy()
		cl["vals"] = []
		db.append(cl)

	for line in src:
		if len(line) < 32: continue
		line = line[:-1].split()[0].lower()
		if len(line) > 32: continue
		N += 1
		for cl in db:
			cl["vals"].append(int(line[cl["start"]/4:cl["stop"]/4], 16))

	return db, N

###################################### pretty-printers

def ppcnt(pcnt): return "%7.2f%%" % (pcnt)

def pp(vals, counts, N):
	if len(counts) == 0: return False
	rv = False

	# print starting from top-freq
	indexer = counts.argsort()[::-1]
	for u,c in zip(vals[indexer], counts[indexer]):
		pcnt = 100.0*c/N
		if pcnt < 0.005: continue

		fmt1 = "%0" + str(L/4) + "x"
		fmt2 = " "*(2+32-L/4) + "%" + "s"
		print ("  " + fmt1 + fmt2) % (u, ppcnt(100.0*c/N))
		rv = True
	return rv

def rpp(vals, counts, L, N):
	if len(counts) == 0: return False
	rv = False

	# print heavy-hitters
	if len(counts) > 4:
		q1, q3 = np.percentile(counts, [25, 75])
		T = min(0.1*N, max(q3 + 1.5*(q1 - q1), 0.02*N))
		hhs = counts > T
		rv = pp(vals[hhs], counts[hhs], N)
		vals = vals[~hhs]
		counts = counts[~hhs]

	pcnt = 100.0 * sum(counts)/N
	if pcnt < 0.05: return rv

	if len(vals) < 5:
		rv |= pp(vals, counts, N)
	else:
		fmt1 = "* %0" + str(L/4) + "x" + "-%0" + str(L/4) + "x"
		fmt2 = " "*(1+32-L/4-L/4-1) + " %" + "s"
		print (fmt1 + fmt2) % (vals.min(), vals.max(), ppcnt(pcnt))
		rv = True

	return rv

###################################### custom DBSCAN metrics

def metric(p1,p2):
	bdiff = math.fabs(p2[0] - p1[0])
	pdiff = math.fabs(math.log(p2[2],13) - math.log(p1[2],13))
	return bdiff*0.25 + pdiff*50.0

###################################### main

## prepare: read segments and IPs
if args.segment:
	segments = read_segment(args.segment)
else:
	segments = read_segments(open(args.segments))

db,N = read_ips(open(args.ips), segments)

## for each segment...
for cn,cl in enumerate(db):
	L = cl["stop"] - cl["start"]
	P = 1.0/2**L
	print "%s: bits %d-%d (hex chars %2d-%2d)" \
		% (SL[cn], cl["start"], cl["stop"], cl["start"]/4+1, cl["stop"]/4)

	### sample IPs if dataset too large?
	if len(cl["vals"]) > 50000:
		vals = np.random.choice(cl["vals"], size=50000)
	else:
		vals = np.asarray(cl["vals"])

	N = len(vals)
	unique,counts = np.unique(vals, return_counts=True)

	### detect frequency top-outliers (@1)
	if len(counts) > 10:
		q1, q3 = np.percentile(counts, [25, 75])
		iqr = q3 - q1
		T = min(0.1*N, max(q3 + 1.5*iqr, 1.0*P*N))
		hhs = counts > T
		nhhs = ~hhs

		# too many? use top 10th as *threshold*
		if sum(hhs) > 10:
			indexer = counts.argsort()[::-1]
			t10 = max(2, counts[indexer[9]])
			hhs = counts >= t10
			nhhs = ~hhs

			# still too many? just use the top 10
			if sum(hhs) > 10:
				hhs = indexer[0:10]
				nhhs = indexer[10:]
	else: # frequency table very short: take all >0.1%
		hhs = counts > max(2, 0.001*N)
		nhhs = ~hhs

	# divide into outliers vs. non-outliers
	hhunique = unique[hhs]
	hhcounts = counts[hhs]
	unique2 = unique[nhhs]
	counts2 = counts[nhhs]

	# present (sorted by counts)
	pp(hhunique, hhcounts, N)

	# anything significant left?
	if sum(counts2) < 0.001*N:
		continue
	elif len(counts2) < 5:
		pp(unique2, counts2, N)
		continue

	### find dense regions (@2)
	if L >= 8:
		dbscan = DBSCAN(eps=(L/4.0)**3.0, min_samples=5)
		regions = dbscan.fit_predict(unique2.reshape(-1,1))
		labels = set(regions)
		left = sum(counts2)

		for label in labels:
			rvals = unique2[regions == label]
			rcounts = counts2[regions == label]

			# anything significant?
			if label == -1:
				continue
			elif sum(rcounts) < 0.001*N:
				regions[regions == label] = -1
				continue

			# find density
			observedc = float(sum(rcounts))
			expectedc = float(rvals.max() - rvals.min()) / (2**L-1) * left
			density = observedc / expectedc
			if density < 100.0:
				regions[regions == label] = -1
				continue

			rpp(rvals, rcounts, L, N)

		unique3 = unique2[regions == -1]
		counts3 = counts2[regions == -1]
	else:
		unique3 = unique2
		counts3 = counts2

	### find continuous regions of similar probability (@3)
	if L >= 8 and len(counts3) > 1:
		bincount = min(256, 2**(cl["stop"]-cl["start"]))
		hist,bins = np.histogram(unique3, weights=counts3, bins=bincount)
		step = bins[1] - bins[0]

		data = np.asarray((range(0,len(hist)), bins[:-1], 1.0*hist/N)).T
		data = data[data[:,2] > 0.0]

		dbscan = DBSCAN(eps=5.0, min_samples=5, metric=metric)
		regions = dbscan.fit_predict(data)
		labels = set(regions)

		cregions = []
		for label in labels:
			rbins  = data[regions == label,1]
			rfreqs = data[regions == label,2]

			# unlabeled: just background
			if label == -1: continue

			# anything significant?
			if len(rbins) < 5 or sum(rfreqs) < 0.1:
				regions[regions == label] = -1
				continue

			start = rbins.min()
			stop  = rbins.max() + step
			avg   = rfreqs.mean()
			cregions.append((start, stop, avg))

		# convert clusters to ranges
		if len(cregions) > 0:
			cregions = np.array(cregions)
			cregions = list(cregions[np.argsort(cregions[:,0])])

			i = 0
			while i+1 < len(cregions):
				cur = cregions[i]
				nxt = cregions[i+1]

				if nxt[0] < cur[1]:
					if nxt[2] > cur[2]:
						if cur[1] > nxt[1]:
							cregions.insert(i+2, np.array([nxt[1], cur[1], cur[2]]))
						cur[1] = nxt[0]
					else:
						nxt[0] = cur[1]
				i += 1

			# print real ranges + probability
			for cregion in cregions:
				indexer = (unique3 >= cregion[0]) & (unique3 <= cregion[1])
				rvals = unique3[indexer]
				rcounts = counts3[indexer]
				if rpp(rvals, rcounts, L, N):
					unique3 = unique3[~indexer]
					counts3 = counts3[~indexer]

	### print the rest (@4)
	pcnt = 100.0 * counts3.sum() / N
	rpp(unique3, counts3, L, N)
