#!/usr/bin/env python
#
# Decodes reduced IPv6 addresses into full hex ip format
#
# Mind the different terminology vs. the paper.
# Runs in python2.
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

import sys
import argparse
import random

p = argparse.ArgumentParser(description='Entropy/IP: decode IPv6 addresses')
p.add_argument('encoded', help='file with reduced addresses')
p.add_argument('analysis', help='output of a2-mining.py')
p.add_argument('--letters', action='store_true', help='decode using letters')
p.add_argument('--colons', action='store_true', help='use colons in output')
p.add_argument('--debug', action='store_true', help='use debug output format')
args = p.parse_args()

def read_segments(src):
	segments = []
	sname = None
	sbits = []
	scodes = []

	for line in src:
		d = line.split()
		if line[0].isalpha():
			# new segment - save old first
			if sname: segments.append({"name": sname, "start": sbits[0], "stop": sbits[1], "codes": scodes})
			sname = d[0][:-1]
			sbits = [int(x) for x in d[2].split('-')]
			scodes = []
		elif line[0] == ' ':
			scodes.append(d[0])
		elif line[0] == '*':
			r = [int(x,16) for x in d[1].split('-')]
			scodes.append((r[0], r[1]))
		else: raise Exception("parse error: " + line)

	segments.append({"name": sname, "start": sbits[0], "stop": sbits[1], "codes": scodes})
	return segments

def decode(val, s):
	global args

	vlen = (s["stop"] - s["start"]) / 4
	C = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", \
	     "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", \
	     "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

	# decode
	if args.letters:
		code = C.index(val)
	else:
		code = int(val) - 1
	if code >= len(s["codes"]): return "?" * vlen

	# just static value?
	val = s["codes"][code]
	if type(val) == str: return val

	# draw from range of values
	# FIXME: to be precise, we would have to avoid drawing the value below from any of the ranges
	# defined in previous segment values; that is, if any of the segment values with lower code
	# defines a range, we should remove it from the random choice below; anyway, we assume the error
	# introduced by this simplified, inaccurate procedure is acceptable for our current applications
	num = random.randint(val[0], val[1])
	fmt1 = "%0" + str(vlen) + "x"
	return fmt1 % num

######

segments = read_segments(open(args.analysis))

for line in open(args.encoded):
	if line[0] == '#': continue
	codes = []

	if args.letters:
		vals = line.strip()
	else:
		vals = line.strip().split(',')

	for val,segment in zip(vals, segments):
		if args.debug:
			codes.append("%s%s=%s\t" % (segment["name"], val, decode(val, segment)))
		else:
			codes.append(decode(val, segment))

	full = "".join(codes)
	if args.colons and not args.debug:
		print ":".join([full[x:x+4] for x in range(0, 32, 4)])
	else:
		print full
