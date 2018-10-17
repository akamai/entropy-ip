#!/usr/bin/env python
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski

import sys
import argparse
import toposort
import json

p = argparse.ArgumentParser(description='rewrite bnfinder CPD to JSON')
p.add_argument('cpd', help='bnfinder cpd Python file')
args = p.parse_args()

# read CPDs
CPD = eval(open(args.cpd).read())

# topological sort of graph dependencies
order = toposort.toposort_flatten({k:set(v['pars']) for k,v in CPD.iteritems()})

CPD2 = {"ORDER": order}

for i,V in enumerate(order):
	vertex = CPD[V]
	vertex2 = CPD2[V] = {}

	# parent list
	vertex2['parents'] = vpars = vertex['pars']

	# children
	vertex2['children'] = []
	for W in order[i+1:]:
		if V in CPD[W]['pars']:
			vertex2['children'].append(W)

	# values
	vertex2['values'] = vvals = vertex['vals']

	# probabilities for different parent values
	vertex2['cpd'] = vcpd = {}
	for parvals,probs in vertex['cpds'].iteritems():
		if parvals == None:
			vcpd["*"] = [probs] * len(vvals)
		else:
			# rewrite the key
			key = ",".join([CPD[par]['vals'][parval] for par,parval in zip(vpars, parvals)])

			# rewrite the values
			kprobs = [probs[None]] * len(vvals)
			for pv,pp in probs.iteritems():
				if pv == None: continue
				kprobs[pv] = pp

			vcpd[key] = kprobs

print "CPD = %s" % (json.dumps(CPD2, indent=1, sort_keys=True))

