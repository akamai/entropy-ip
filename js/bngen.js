/*
 * Bayes Net generator wrt to global CPD
 *
 * Copyright (c) 2015-2016 Akamai Technologies, Inc.
 * See file "LICENSE" for licensing information.
 * Author: Pawel Foremski
 */

R.bngen = {
	sample: function(count)
	{
		var ret = [];
		var N = count > 0 ? count : 1;

		for (var i = 0; i < N; i++) {
			var obs = {};
			var arr = [];

			CPD["ORDER"].forEach(function(V)
			{
				// construct the query
				var query = [];
				CPD[V]["parents"].forEach(function(P){ query.push(obs[P]); });

				// get the adequate cpd
				var qstr = query.join();
				var cpd = (qstr in CPD[V]["cpd"]) ? CPD[V]["cpd"][qstr] : CPD[V]["cpd"]["*"];

				// toss the coin
				var probT = Math.random();
				var valid;
				for (valid = 0; valid < cpd.length; valid++) {
					probT -= cpd[valid];
					if (probT <= 0) break;
				}
				if (valid >= cpd.length) valid = cpd.length - 1;

				// translate and save
				arr.push(obs[V] = CPD[V]["values"][valid]);
			});

			ret.push(arr);
		}

		return ret;
	},

	/** Generate Probability Distribution for all variables, optionally conditioned on evidence */
	cpd: function(sample, evidence)
	{
		var cpd = {};
		var order = CPD["ORDER"];
		var E = [];

		// initialize cpd
		order.forEach(function(V)
		{
			cpd[V] = [];
			CPD[V]["values"].forEach(function(val){ cpd[V][val] = 0; });
		});

		cpd._total = sample.length;
		cpd._count = 0;
		cpd._tries = 1;   // for cache
		cpd._sample = []; // for genIP

		// initialize E?
		if (evidence) {
			$.each(evidence, function(V, accepted)
			{
				if (!$.isArray(accepted)) accepted = [accepted];
				$.each(accepted, function(i, val) { accepted[i] = String(val); });
				if (accepted.length > 0) E[order.indexOf(V)] = accepted;
			});
		}

		// count values
		sample.forEach(function(ip)
		{
			// filter via E
			for (var pos in E)
				if (!E[pos].includes(ip[pos])) return;

			// count
			for (var j = 0; j < ip.length; j++) cpd[order[j]][ip[j]]++;

			cpd._count++;
			if (cpd._count < 1000) cpd._sample.push(ip);
		});

		// normalize
		if (cpd._count > 1) order.forEach(function(V)
		{
			cpd[V].forEach(function(count, code){ cpd[V][code] = count / cpd._count; });
		});

		return cpd;
	},

	cache: function(evidence, cpd)
	{
		var db = R.bngen._cachedb;
		var evkey = JSON.stringify(evidence);

		/* new in cache? */
		if (!(evkey in db)) {
			if (!cpd) return null;
			else      return db[evkey] = cpd;
		}

		// fetch from cache
		var edb = db[evkey];
		if (cpd === undefined) return edb;

		// update
		edb._tries++;
		edb._total += cpd._total;
		if (cpd._count == 0) return edb;
		edb._sample = edb._sample.concat(cpd._sample);

		/* integrate new data */
		var sum = edb._count + cpd._count;
		var w1  = edb._count / sum;
		var w2  = cpd._count / sum;
		$.each(edb, function(V, ecpd)
		{
			if (V[0] == "_") return;
			ecpd.forEach(function(prob, val) { ecpd[val] = prob*w1 + cpd[V][val]*w2; });
		});

		edb._count = sum;
		return edb;
	},
	_cachedb: {},

	genIP: function(cache, n)
	{
		if (cache._sample.length < 3) return [];

		var ret = [];
		for (var i = 0; i < n; i++) {
			var ip;
			do {
				ip = cache._sample[Math.floor(Math.random() * cache._sample.length)];
			} while(!ip)

			var str = "";
			ip.forEach(function(code, Vi)
			{
				var V = CPD["ORDER"][Vi];
				str += "" + V + code + "=" + VALS[V].codes[code][0] + "\t";
			});

			var ipvals = [];
			ip.forEach(function(code, Vi)
			{
				var V = CPD["ORDER"][Vi];

				// decode
				var val = VALS[V].codes[code][0];
				if (val.includes("-")) { // draw from range?
					var sv = val.split("-");
					var min = parseInt(sv[0], 16);
					var max = parseInt(sv[1], 16);
					var dv  = Math.floor(Math.random() * (max - min + 1)) + min;
					val = dv.toString(16);

					// add padding?
					var len = Math.floor((VALS[V].stop - VALS[V].start) / 4);
					for (var l = val.length; l < len; l++) val = "0" + val;
				}

				ipvals[VALS["ORDER"].indexOf(V)] = val;
			});

			// pretty-print
			var str  = ipvals.join("");
			var str4 = "";
			for (var j = 0; j < str.length; j += 4) str4 += str.slice(j, j + 4) + ":";
			ret.push(str4.slice(0, -1));
		}

		return ret;
	},
};
