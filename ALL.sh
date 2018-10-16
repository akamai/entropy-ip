#!/bin/bash

function ips()
{
	if [ "${IPS##*.}" = "gz" ]; then
		cat $IPS | zcat
	else
		cat $IPS
	fi
}

if [ $# -ne 2 ]; then
	echo "usage: ALL.sh ips target"
	echo
	echo "Entropy/IP: do all steps to prepare a web report on set of IPv6 addrs"
	echo
	echo "  ips         IPv6 addresses in hex ip format"
	echo "  target      target directory for the report"
	exit 1
fi >&2

IPS="$1"
DIR="$2"

set -o pipefail
set -o errexit
set -o nounset

mkdir -p $DIR
[ -d "$DIR" ] || exit 1

echo "1. segments"
ips | ./a1-segments.py /dev/stdin \
	>$DIR/segments || exit 2

echo -e "\n2. segment mining"
ips | ./a2-mining.py /dev/stdin $DIR/segments \
	>$DIR/analysis || exit 3

echo -e "\n3. bayes model"
ips | ./a3-encode.py /dev/stdin $DIR/analysis \
	| ./a4-bayes-prepare.sh /dev/stdin \
	>$DIR/bnfinput || exit 4
./a5-bayes.sh $DIR/bnfinput \
	>$DIR/cpd || exit 5

echo -e "\n4. web report"
./b1-webreport.sh $DIR $DIR/segments $DIR/analysis $DIR/cpd \
	|| exit 6

exit 0
