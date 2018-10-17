/*
 * BN structure visualization in vis.js
 *
 * Copyright (c) 2015-2016 Akamai Technologies, Inc.
 * See file "LICENSE" for licensing information.
 * Author: Pawel Foremski
 */

R.bnviz = {
	net: undefined,

	init: function(el)
	{
		if (!el) return;

		var nodes = [], edges = [];
		$.each(VALS["ORDER"], function(id, V)
		{
			nodes.push({
				id: id,
				label: V,
				x: id*100,
				y: id*40,
				color: {border:'black', background:'white', highlight:{border:'red',background:'white'}},
				font:  { size: 20 },
			});

			$.each(CPD[V]["children"], function(i, V2)
			{
				edges.push({
					from: id,
					to: VALS["ORDER"].indexOf(V2),
					arrows: "to",
					smooth: { type: 'vertical', roundness: 1.0 },
					color: { color:'black', highlight: 'red' },
					selectionWidth: 2,
				});
			});
		});

		var lopts = {
			randomSeed: 0,
			hierarchical: false,
		};

		var iopts = {
			dragView: false,
			multiselect: true,
			zoomView: false,
		};

		// draw
		R.bnviz.net = new vis.Network(
			document.getElementById(el),
			{ nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
			{ layout: lopts, interaction: iopts, physics: {enabled: false}}
		);
	},

	update: function(query)
	{
		var net = R.bnviz.net;
		if (!net) return;

		net.unselectAll();
		var nodes = [];
		$.each(query, function(V, values) { nodes.push(VALS["ORDER"].indexOf(V)); });
		net.selectNodes(nodes);
	},
};
