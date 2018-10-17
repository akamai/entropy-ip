#!/bin/bash
#
# This code implements the Bayes Net modeling in Entropy/IP
# Runs in bash, requires bnfinder (http://bioputer.mimuw.edu.pl/software/bnf/)
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

if { [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; }; then
	echo "usage: ./4-bayes.sh bnfinput > cpd"
	echo
	echo "Entropy/IP: use BNFinder to build a Bayes Net model for IPv6 addrs"
	echo
	echo "  bnfinput     output of a4-bayes-prepare.sh"
	echo
	echo "Copyright (c) 2015-2016 Akamai Technologies, Inc."
	echo "See file LICENSE for licensing information."
	echo "Author: Pawel Foremski"
	exit 1
fi >&2

set -o pipefail
set -o errexit
set -o nounset

echo "Starting bnf (ignore the last line if it says CPD went to /dev/stderr)" >&2
bnf -s BDE -v -k 8 -e "$1" -c /dev/stderr 3>&2 2>&1 1>&3
