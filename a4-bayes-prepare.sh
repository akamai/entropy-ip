#!/bin/bash
#
# This code rewrites encoded IPs into the BNFinder input format
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

if { [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; }; then
	echo "usage: ./4-bayes-prepare.sh encoded > bnfinput" >&2
	echo "" >&2
	echo "Entropy/IP: rewrite encoded IPv6 addrs into BNFinder format" >&2
	echo "" >&2
	echo "  encoded     file with encoded IPv6 addresses (output for a3-encode.py)" >&2
	exit 1
fi

set -o pipefail
set -o errexit
set -o nounset

cat "$1" | ./bin/rewrite-bnf.py
