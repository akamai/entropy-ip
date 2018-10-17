#!/usr/bin/env python
#
# This code rewrites data to BNFinder-suitable input
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

import sys
import argparse
import numpy as np

p = argparse.ArgumentParser(description='Entropy/IP: rewrite to BNFinder')
p.add_argument('--full', action='store_true', help='take full dataset instead of 100K sample')
args = p.parse_args()

a = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", \
     "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
db = {}

lines = []
for line in sys.stdin:
	lines.append((int(x) for x in line.split(',')))

if not args.full and len(lines) > 100000:
	lines = np.random.choice(lines, size=100000)

for line in lines:
	for key,v in enumerate(line):
		if key not in db: db[key] = []
		db[key].append(v)

for key in sorted(db.keys()):
	vals = set(db[key])
	print "#discrete %s %s" % (a[key], " ".join(["%d"%x for x in vals]))
	print "#parents %s %s" % (a[key], " ".join([a[x] for x in range(key)]))

for key in sorted(db.keys()):
	if key == 0:
		print "exp " + " ".join(["L%d"%(x+1) for x in range(len(db[key]))])

	print a[key] + " " + " ".join(["%d"%x for x in db[key]])
