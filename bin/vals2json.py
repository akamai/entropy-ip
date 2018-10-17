#!/usr/bin/env python
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski

import sys
import argparse
import json
import re

p = argparse.ArgumentParser(description='convert vals to JSON')
p.add_argument('values', help='output of analyze.py')
p.add_argument('--anon', action='store_true')
p.add_argument('--ipv4')
args = p.parse_args()

def read_values(src):
	sections = {}
	sname = None
	sbits = []
	scode = 0
	scodes = [('?',0.)]

	sections["ORDER"] = []
	for line in src:
		d = line.split()

		# new section - save old first
		if line[0].isalpha():
			if sname:
				sections[sname] = { "start": sbits[0], "stop": sbits[1], "codes": scodes}
				sections["ORDER"].append(sname)

			sname = d[0][:-1]
			sbits = [int(x) for x in d[2].split('-')]
			scodes = [('?',0.)]
			continue

		# parse
		if line[0] == ' ':
			scode = [d[0], float(d[1][:-1]) * 0.01]
		elif line[0] == '*':
			scode = [d[1], float(d[2][:-1]) * 0.01]
		else: raise Exception("parse error: " + line)

		desc = scode[0]
		i = len(scodes)

		if args.anon and sname == "A":
			if i < 15: scode[0] = "%x0010db8" % (i+1)
			else:      scode[0] =  "%x010db8" % (i+1)
			if desc.find("-") > 0:
				scode[0] += "-" + scode[0][:-1] + "f"

		if args.ipv4 and sname == args.ipv4:
			if len(desc) == 3:
				scode[0] = "%d"%(126+i)
			else:
				scode[0] = re.sub(r"^0[0-9][1-9][1-9]0", "01270", desc)
				scode[0] = re.sub(r"-0[0-9][1-9][1-9]0", "-01270", scode[0])

		scodes.append(scode)

	sections[sname] = { "start": sbits[0], "stop": sbits[1], "codes": scodes}
	sections["ORDER"].append(sname)

	return sections

print "VALS = %s" % (json.dumps(read_values(open(args.values)), indent=1))
