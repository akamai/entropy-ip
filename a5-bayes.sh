#!/bin/bash
#
# This code implements the Bayes Net modeling in Entropy/IP
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# Author: Pawel Foremski <pjf@akamai.com>
# Mind the different terminology vs. the paper; excuse the code quality.
# Runs in bash, requires bnfinder (http://bioputer.mimuw.edu.pl/software/bnf/)
#

if { [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; }; then
	echo "usage: ./4-bayes.sh bnfinput > cpd" >&2
	echo "" >&2
	echo "Entropy/IP: use BNFinder to build a Bayes Net model for IPv6 addrs" >&2
	echo "" >&2
	echo "  bnfinput     output of a4-bayes-prepare.sh" >&2
	exit 1
fi

set -o pipefail
set -o errexit
set -o nounset

echo "Starting bnf (ignore the last line if it says CPD went to /dev/stderr)" >&2
bnf -s BDE -v -k 8 -e "$1" -c /dev/stderr 3>&2 2>&1 1>&3
