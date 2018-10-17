#!/usr/bin/env python
#
# This code implements the IPv6 encoding in Entropy/IP
# Mind the different terminology vs. the paper.
# Runs in python2.
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

import sys
import argparse
import math

p = argparse.ArgumentParser(description='Entropy/IP: encode IPv6 addresses')
p.add_argument('ips', help='file with IPv6 addresses in full hex form')
p.add_argument('analysis', help='output of a2-mining.py')
p.add_argument('--letters', action='store_true', help='encode with letters')
p.add_argument('--rcode', action='store_true', help='try to encode unknown values')
args = p.parse_args()

def read_segments(src):
	segments = []
	sname = None
	sbits = []
	scode = 0
	svalues = {}
	sranges = []

	for line in src:
		d = line.split()
		if line[0].isalpha():
			if sname: # new segment - save old first
				segments.append({"name": sname, "rcode": scode,
					"start":  sbits[0], "stop":   sbits[1],
					"values": svalues,  "ranges": sranges})

			sname = d[0][:-1]
			sbits = [int(x) for x in d[2].split('-')]
			scode = 0
			svalues = {}
			sranges = []

		elif line[0] == ' ':
			v = int(d[0], 16)
			svalues[v] = scode
			scode += 1

		elif line[0] == '*':
			r = [int(x,16) for x in d[1].split('-')]
			sranges.append((r[0], r[1], scode))
			scode += 1

		else: raise Exception("parse error: " + line)

	segments.append({"name": sname, "rcode": scode,
		"start":  sbits[0], "stop":   sbits[1],
		"values": svalues,  "ranges": sranges})
	return segments

def encode(val, s):
	global args
	if args.letters:
		C = lambda x: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", \
		     "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", \
		     "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"][x]
	else:
		C = lambda x: "%d"%(x+1)

	if val in s["values"]:
		return C(s["values"][val])

	for r in s["ranges"]:
		if val >= r[0] and val <= r[1]:
			return C(r[2])

	if args.rcode:
		return C(s["rcode"])
	else:
		return '?'

######

segments = read_segments(open(args.analysis))

for line in open(args.ips):
	codes = []

	for s in segments:
		val = int(line[s["start"]/4:s["stop"]/4], 16)
		codes.append(encode(val, s))

	if '?' in codes:
		continue
	elif args.letters:
		print "".join(codes)
	else:
		print ",".join(codes)
