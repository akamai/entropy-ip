/*
 * BN Browser
 *
 * Copyright (c) 2015-2016 Akamai Technologies, Inc.
 * See file "LICENSE" for licensing information.
 * Author: Pawel Foremski
 */

var R = {};
var $R = null;

R.bnbrowser = {
	init: function(root, viz)
	{
		// init
		$R = root;
		R.bn6draw.init();

		// show basic view
		R.bnbrowser.query({});

		// visualize the structure?
		if (viz) R.bnviz.init(viz);
	},

	_query: {},
	_lastdraw: 0,
	query: function(query, n, count, tries, ips)
	{
		var cpd, cache;
		var drawn = false;

		if (query === undefined) {
			query = R.bnbrowser._query;
			if (!n) n = 3000;
		} else {
			R.bnbrowser._query = query;
			R.bnviz.update(query);
			if (!n) n = 1000;
		}

		if (!count) count = 10000;
		if (!tries) tries = 50;
		if (!ips) ips = 50;

		R.bn6draw.status_est("Estimating...");
		R.bn6draw.status_prob("");
		R.bn6draw.status_ips("");

		// cache not good enough?
		cache = R.bngen.cache(query);
		if (!cache || cache._count < count) {
			cpd    = R.bngen.cpd(R.bngen.sample(n), query);
			cache  = R.bngen.cache(query, cpd);
		}

		if (Date.now() - R.bnbrowser._lastdraw > 500) {
			R.bn6draw.update(cache);
			R.bnbrowser._lastdraw = Date.now();
		}

		// need to schedule updates?
		if (cache._count < count && cache._tries < tries) {
			setTimeout(R.bnbrowser.query, 0, undefined, n, count, tries, ips);
		} else {
			if (!drawn) R.bn6draw.update(cache);

			if (cache._count > 0) {
				var prob = cache._count / cache._total * 100;
				R.bn6draw.status_est("Estimated for n=" + cache._count + " (click to improve)");
				R.bn6draw.status_prob("Combination probability: "
					+ prob.toFixed(2) + "% (in " + cache._total + ")");
				R.bn6draw.status_ips(R.bngen.genIP(cache, ips).join("\n"));
			} else {
				R.bn6draw.status_est("Combination not found (click to keep searching)");
				R.bn6draw.status_prob("No instance in " + cache._total);
			}
		}
	},
	query_improve: function()
	{
		var query = R.bnbrowser._query;
		var cache = R.bngen.cache(query);
		if (!cache) return;

		var count = Math.round(1.25 * cache._total);
		var tries = Math.round(1.50 * cache._tries);
		var ips   = Math.max(1000, Math.min(5000, count));
		R.bnbrowser.query(undefined, 10000, count, tries, ips);
	},
};
