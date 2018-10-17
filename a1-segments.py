#!/usr/bin/env python
#
# This code implements the first steps of the Entropy/IP algorithm:
#   @1 computes per-nybble entropy across the IPv6 dataset
#   @2 computes 4-bit Aggregation Count Ratios
#   @3 finds address segments using entropy thresholds
#
# Mind the different terminology vs. the paper.
# Runs in python2. Requires numpy.
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

import sys
from collections import defaultdict
import argparse
import math
import numpy as np

p = argparse.ArgumentParser(description='Entropy/IP: entropy and segmenting')
p.add_argument('ips', help='file with IPv6 addresses in full hex form')
p.add_argument('--size', type=int, default=32, help='total address length in nybbles [32]')
p.add_argument('-S', type=int, default=1, help='step size in nybbles [1]')
p.add_argument('--isp', type=int, default=8, help='ISP prefix size in nybbles [8]')
p.add_argument('--net', type=int, default=16, help='network id size in nybbles [16]')
p.add_argument('--noacr', action='store_true', help='skip Aggregate Count Ratios')
args = p.parse_args()

AL = args.size / args.S

### prepare: read ips and count occurances of nybble values
IPS = []
DB = {}
N = 0.0

for pos in range(0, AL+1):
	DB[pos] = defaultdict(int)

for line in open(args.ips):
	if len(line) < 32: continue
	s = line[:-1].split()[0].lower()
	IPS.append(s)
	for pos,val in enumerate([s[i:i+args.S] for i in range(0, len(s), args.S)]):
		DB[pos][val] += 1
	N += 1.0

#### analyze (@1, @2)
METRICS = {}
previous = 0

print "# N\t%d" % N
print "## POS\tSTART\tignore\tENT\tACR"
for pos in range(0, AL):
	d = DB[pos]

	# find individual entropy and probabilities
	ENT = 0.0
	for pattern in d.keys():
		p = float(d[pattern]) / N
		ENT -= p * math.log(p,2)
	ENT /= 4.0*args.S

	# ACR
	db = {}
	stop = (pos + 1)*args.S
	if not args.noacr:
		for ip in IPS: db[ip[0:stop]] = True
	c = len(db.keys())
	ratio = float(c) / previous if previous > 0 else 1.0
	ACR = (ratio - 1.0) / (2**(4*args.S) - 1.0)
	previous = c

	print "%d\t%3d\t%5.3f\t%5.3f\t%5.3f" % \
		((pos*args.S)+1, pos*args.S*4, 0.0, ENT, ACR)

	METRICS[pos] = (ENT, ACR)

### find segments (@3)
cs = 0
lt = -1
le = -1.
ents = []

print "##        \tTYPE\tSTART\tSTOP\tAVG ENT"
for pos in range(0, AL):
	(ENT, ACR) = METRICS[pos]

	if pos < args.isp / args.S:
		ents.append(ENT)
		continue

	# classify
	if ENT < 0.025:
		t = 1
	elif ENT < 0.1:
		t = 2
	elif ENT < 0.3:
		t = 3
	elif ENT < 0.5:
		t = 4
	elif ENT < 0.9:
		t = 5
	else:
		t = 6

	# divide?
	if pos == args.isp / args.S:
		d = True
	elif pos == args.net / args.S:
		d = True
	elif lt > 0 and t != lt and abs(ENT - le) > 0.05:
		d = True
	else:
		d = False

	if d and len(ents) > 0:
		print "# segment\tt%d\t%3d\t%3d\t%.3f" % \
			(lt, (cs*args.S)*4, pos*args.S*4, np.mean(ents))
		cs = pos
		ents = []

	ents.append(ENT)
	lt = t
	le = ENT

print "# segment\tt%d\t%3d\t%3d\t%.3f" % \
	(lt, (cs*args.S)*4, AL*args.S*4, np.mean(ents))
