#!/usr/bin/env python
#
# Generates reduced IPv6 addresses out of an Entropy/IP model
#
# Note that this code is probably not the fastest possible. For larger tasks it might
# be reasonable to optimize it first, or use a different Bayes Net technique.
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# Author: Pawel Foremski <pjf@akamai.com>
# Mind the different terminology vs. the paper; excuse the code quality.
# Runs in python2. Requires toposort (https://pypi.python.org/pypi/toposort)
#

import sys
import argparse
import toposort
import random

p = argparse.ArgumentParser(description='Entropy/IP: generate reduced IPv6 addrs')
p.add_argument('cpd', help='file with the Bayes net model (output a4-bayes.sh)')
p.add_argument('-n', type=int, default=10, help='number of IPs to generate')
args = p.parse_args()

# read CPDs
CPD = eval(open(args.cpd).read())

# topological sort of graph dependencies
order = toposort.toposort_flatten({k:set(v['pars']) for k,v in CPD.iteritems()})
print "# " + ", ".join(sorted(order))

# generate!
i = 0
while args.n <= 0 or i < args.n:
	i += 1
	chosen = {}
	vals = {}

	for V in order:
		vertex = CPD[V]

		# query the CPD wrt evidence
		query = tuple([chosen[P] for P in vertex['pars']])
		if query in vertex['cpds']:
			pd = vertex['cpds'][query]
		else:
			pd = {None: vertex['cpds'][None]}

		# take random selection
		cprob = random.random()
		ks = set(range(len(vertex['vals'])))
		for k,prob in pd.iteritems():
			if k == None: continue
			cprob -= prob
			if cprob <= 0: break
			else: ks.remove(k)
		else:
			# choose randomly from not specified so far
			if len(ks) > 0:
				k = random.choice(list(ks))
			else:
				k = random.choice(range(len(vertex['vals'])))

		# translate and store
		vals[V] = vertex['vals'][k]
		chosen[V] = k

	print ",".join([vals[k] for k in sorted(vals.keys())])
