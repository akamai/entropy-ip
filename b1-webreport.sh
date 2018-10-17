#!/bin/bash
#
# Generates web report for an Entropy/IP model
#
# Copyright (c) 2015-2016 Akamai Technologies, Inc.
# See file "LICENSE" for licensing information.
# Author: Pawel Foremski
#

if [ $# -ne 4 ]; then
	echo "usage: b1-webreport.sh target segments analysis cpd"
	echo
	echo "Entropy/IP: generate web report in given target dir"
	echo
	echo "  target      path to target directory"
	echo "  segments    output of a1-segments.py"
	echo "  analysis    output of a2-mining.py"
	echo "  cpd         output of a4-bayes.sh"
	echo
	echo "Copyright (c) 2015-2016 Akamai Technologies, Inc."
	echo "See file LICENSE for licensing information."
	echo "Author: Pawel Foremski"
	exit 1
fi >&2

DIR="$1"
SEGMENTS="$2"
ANALYSIS="$3"
CPD="$4"

mkdir -p $DIR
[ -d $DIR ] || exit 1

{
# header
cat <<-EOF
<html>
	<head>
		<title>Entropy/IP report: $DIR</title>
		<style type="text/css">
		ol { margin: 0; }
		h2 { cursor: pointer; font-size: 16px; color: blue; }
		h2:hover { text-decoration: underline; }
		textarea { font-family: courier; font-size: 14px; }
		</style>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<link rel="stylesheet" type="text/css" media="all" href="../css/bnbrowser.css" />
		<link rel="stylesheet" type="text/css" media="all" href="../css/colors-jet.css" />
		<link rel="stylesheet" type="text/css" media="all" href="../css/vis.min.css" />
	</head>
	<body>
	<h1 align="center">Entropy/IP report: $DIR</h1>
EOF

# entropy vs ACR
cat $SEGMENTS | ./bin/plot-entvsmra.py --save $DIR/segments.png >/dev/null
echo "<h2 align=\"center\">Entropy vs. ACR</h2>"
echo "<center><img src=\"segments.png\" /></center>"

# segment mining
echo "<h2 align=\"center\">Segment Mining</h2>"
echo "<center>"
echo "<pre style=\"font-size:14px; display: inline-block; text-align: left\">"
echo "<ol style='display:none'>"
cat $ANALYSIS | while read line; do
	if [[ $line =~ ^[A-Z]: ]]; then
		echo "</ol>"
		echo -n "<b style='color:#c00'>$line</b>"
		echo -n "<ol>"
	elif [[ $line =~ ^\* ]]; then
		echo -n "<li><i style='color:#080'>$line</i></li>"
	else
		echo -ne "<li>  $line</li>"
	fi
done
echo "</ol>"
echo "</pre>"
echo "</center>"

# bayes net
./bin/cpd2json.py $CPD > $DIR/cpd.js
./bin/vals2json.py $ANALYSIS > $DIR/vals.js
cat <<-EOF
<h2 align="center">Bayesian Network Structure</h2>
<center>
<div id="bnviz"></div>
</center>

<h2 align="center">Conditional Probability Browser</h2>
<center>
<div id="bnbrowser" style="width: 1000px">
	<table class="bnb-main">
		<tr class="bnb-vars"></tr>
		<tr class="bnb-vdsc"></tr>
		<tr class="bnb-vals"></tr>
	</table>
	<div class="bnb-status">Loading...</div>
	<form>
		<textarea class="bnb-ips" name="ips"></textarea>
	</form>
</div>
</center>

<script type="text/javascript" src="vals.js"></script>
<script type="text/javascript" src="cpd.js"></script>
<script type="text/javascript" src="../js/jquery-2.2.0.min.js"></script>
<script type="text/javascript" src="../js/json2.js"></script>
<script type="text/javascript" src="../js/vis.min.js"></script>
<script type="text/javascript" src="../js/bnbrowser.js"></script>
<script type="text/javascript" src="../js/bngen.js"></script>
<script type="text/javascript" src="../js/bn6draw.js"></script>
<script type="text/javascript" src="../js/bnviz.js"></script>
<script type="text/javascript">
\$(document).ready(function() {
	R.bnbrowser.init(\$("#bnbrowser"), 'bnviz');
	//\$('h2').next().hide();
});
\$('h2').click(function(e)
{
	\$(e.target).next().slideToggle();
});
</script>

	<h3>Generated on `date`</h3>
	</body>
</html>
EOF
} >$DIR/index.html

echo "report written to $DIR/index.html"
