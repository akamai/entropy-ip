#!/usr/bin/env python
#
# Entropy/IP: draw Entropy vs ACR plot
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# Author: Pawel Foremski <pjf@akamai.com>
# Runs in python2. Requires matplotlib
#

import sys
import matplotlib.pyplot as plt
import argparse
import math

# restore matplotlib 1 style
import matplotlib.style
import matplotlib as mpl
mpl.style.use('classic')

p = argparse.ArgumentParser()
p.add_argument("--title")
p.add_argument('--labels')
p.add_argument('--save')
p.add_argument('--ylim')
p.add_argument('--nc', action='store_true')
p.add_argument('--optim', action='store_true')
args = p.parse_args()

def get(src):
	# read data
	data = []
	segments = []
	for line in src:
		if line[0:10] == "# segment\t":
			d = line[0:-1].split('\t')
			row = {
				"start": int(d[2]),
				"stop":  int(d[3]),
				"avg": float(d[4])
			}
			segments.append(row)
		elif line[0] != '#':
			data.append(line[0:-1].split('\t'))

	bit = [int(r[1]) for r in data]
	ent = [float(r[3]) for r in data]
	mra = [float(r[4]) for r in data]

	s = bit[1] - bit[0]
	for i,v in enumerate(bit): bit[i] += s
	bit.insert(0, 0)
	ent.insert(0, ent[0])
	mra.insert(0, mra[0])

	return (bit,ent,mra,segments)

#####

fig = plt.figure()
if args.optim:
	ax1 = plt.subplot2grid((4,1), (0,0), rowspan=2)
else:
	ax1 = fig.add_subplot(111)
if args.title: ax1.set_title(args.title, y=1.04)
ax1.set_xlabel("Prefix length / Hex char location (bits)")
ax1.set_ylabel("Normalized value")

ax1.set_xlim([0, 128])
if args.optim:
	ax1.set_ylim([-.02, 1.02])
else:
	ax1.set_ylim([-.005, 1.005])
if args.ylim: ax1.set_ylim([float(x) for x in args.ylim.split(',')])

ax1.set_xticks([0,16,32,48,64,80,96,112,128])
plt.grid()

if args.labels: labels = args.labels.split(',')
else: labels = ["Entropy", "4-bit ACR"]

#####

x,ent,mra,segments = get(sys.stdin)
s = "%s ($\hat{H}_S=%.1f$)"
es = sum(ent[1:])

ax1.plot(x,ent, 'b', lw=2.7, drawstyle='steps', label=s%(labels[0],es))
ax1.plot(x,mra, 'r--', lw=2.7, drawstyle='steps', label=labels[1])

if args.nc == False:
	bb = ax1.get_position()
	a = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", \
		 "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
	c = '#220000'

	for i,segment in enumerate(segments):
		if segment["stop"] < 128:
			ax1.axvline(segment["stop"], c=c, ls='--', lw=1.2, zorder=5)
		middle = ((segment["start"] + segment["stop"]) / 2.) / 128.
		plt.figtext(bb.xmin + middle*bb.width - 0.007, 0.905, a[i], \
			color=c, style='italic')

#####

if args.nc :
	ax1.legend(loc=(0.76, 0.05))
else:
#	ax1.legend(loc=(0.01, 0.85))
	ax1.legend(loc='best')

if args.save:
	plt.savefig(args.save)
	sys.stdout.write("Saved to %s\n" % (args.save))
else:
	plt.show()
