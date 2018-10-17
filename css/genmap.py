#!/usr/bin/env python
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski

from matplotlib import cm
import numpy as np
import math

def minmax(Min, Max, Val): return max(Min, min(Max, Val))

txtmap = [1.0, 1.0, 1.0, 1.0, 1.0, 0.95, 0.9, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0]

print ".bnb-color-0 { background-color: white; color: #ccc; }"
jet = cm.get_cmap("jet")
for i,color in enumerate(jet(np.linspace(0,1,100))):
	r,g,b,a = color

	background = "#%02x%02x%02x" % (r*255, g*255, b*255)

	# find text lightness
	light = minmax(0.0, 1.0, (1.5*r + g + 0.7*b) / 3.0)
	txt = txtmap[int(round(light * (len(txtmap)-1)))]

	txt = minmax(0.0, 1.0, txt)
	text = "#%02x%02x%02x" % (txt*255, txt*255, txt*255)

	print ".bnb-color-%d { background-color: %s; color: %s; }" % ((i+1), background, text)
