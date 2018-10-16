#!/usr/bin/env python
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# Author: Pawel Foremski <pjf@akamai.com>

import sys
import argparse
import json
import re

p = argparse.ArgumentParser(description='convert JSON to vals')
p.add_argument('values', help='output of vals2json.py')
args = p.parse_args()

def ppcnt(pcnt):
	return "%7.2f%%" % (pcnt*100.0)

def pp(L, val, pcnt):
	fmt1 = "%" + "s"
	fmt2 = " "*(2+32-L/4) + "%" + "s"
	print ("  " + fmt1 + fmt2) % (val, ppcnt(pcnt))

def rpp(L, val, pcnt):
	v = val.split("-")
	fmt1 = "* %"+"s-%"+"s"
	fmt2 = " "*(1+32-L/4-L/4-1) + " %" + "s"
	print (fmt1 + fmt2) % (v[0], v[1], ppcnt(pcnt))


vals = json.loads(open(args.values).read()[7:])

for seg in vals["ORDER"]:
	cl = vals[seg]
	L = cl["stop"] - cl["start"]

	print "%s: bits %d-%d (hex chars %2d-%2d)" \
		% (seg, cl["start"], cl["stop"], cl["start"]/4+1, cl["stop"]/4)

	for code in cl["codes"][1:]:
		val,pcnt = code
		if val.find("-") > 0: rpp(L, val, pcnt)
		else: pp(L, val, pcnt)
