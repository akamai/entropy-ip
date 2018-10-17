/*
 * BN Browser - IPv6
 *
 * Copyright (c) 2015-2016 Akamai Technologies, Inc.
 * See file "LICENSE" for licensing information.
 * Author: Pawel Foremski
 */

R.bn6draw = {
	init: function()
	{
		var $vars = $R.find("tr.bnb-vars");
		var $vdsc = $R.find("tr.bnb-vdsc");
		var $vals = $R.find("tr.bnb-vals");
		var $status = $R.find("div.bnb-status");
		var $e;

		/* draw the main plots */
		VALS["ORDER"].forEach(function(V)
		{
			var d = VALS[V];

			// add columns
			$vars.append('<td id="bnb-var-' + V + '">' + V + '</td>\n');
			$vdsc.append('<td>' + d.start + '-' + d.stop + '</td>\n');
			$vals.append('<td id="bnb-val-' + V + '"></td>\n');

			// add values
			$e = $vals.find("#bnb-val-" + V);
			d.codes.forEach(function(def, code)
			{
				if (code == 0) return;
				$("<div/>", {
					data: {V:V, code:String(code), isrange: def[0].includes("-")},
					id: "bnb-prob-" + V + code,
					class: "bnb-color-0",
					html: def[0].replace("-", "<br />")
				})
					.click(R.bn6draw.click)
					.appendTo($e);
			});
		});

		/* draw the colormap */
		$("<td/>", {
			id: "bnb-clear",
			text: "",
		})
			.click(R.bn6draw.clear)
			.appendTo($vars);

		$e = $("<td/>", {id: "bnb-val-colormap"}).appendTo($vals);
		for (var i = 100; i >= 0; i-=5)
			$e.append('<div class="bnb-colormap bnb-color-' + i + '">' + i + '%</div>');

		/* draw status */
		$status.html("").click(R.bnbrowser.query_improve);
		$("<span/>", { id: "bnb-status-est" }).appendTo($status);
		$("<br/>").appendTo($status);
		$("<span/>", { id: "bnb-status-prob" }).appendTo($status);
	},

	update: function(cdfs)
	{
		$.each(cdfs, function(V, cdf)
		{
			if (V[0] == "_") return;
			$R.find("#bnb-var-"+V).removeClass("bnb-selected");

			cdf.forEach(function(prob, code)
			{
				var $div = $R.find("#bnb-prob-" + V + code);
				var data = $div.data();
//				if (!data) console.log("no data for " + V + code);

				var pcode = Math.floor(prob * 100);

				var cs = ["bnb-color-" + pcode];
				if (data.selected) {
					cs.push("bnb-selected");
					$R.find("#bnb-var-"+V).addClass("bnb-selected");
				}
				if (data.isrange) cs.push("bnb-range");

				$div.attr("class", cs.join(" "));
				$div.attr("title", V+code+", "+(prob*100).toFixed(2) + "%");
			});
		});
	},

	_undoQ: {},
	clear: function(e)
	{
		var Q;
		var $div = $(e.target);

		if ($div.text() == "(clear)") {
			R.bn6draw._undoQ = R.bn6draw._query;
			Q = R.bn6draw._query = {};

			$R.find(".bnb-selected").removeClass("bnb-selected").data("selected", false);
			$div.text("(undo)").css("color", "black");
		} else if ($div.text() == "(undo)") {
			Q = R.bn6draw._query = R.bn6draw._undoQ;

			$.each(Q, function(V, vals)
			{
				vals.forEach(function(code) {
					$("#bnb-prob-"+V+code).addClass("bnb-selected").data("selected", true);
				});
			});
			$div.text("(clear)").css("color", "red");
		}

		R.bnbrowser.query(Q);
	},

	_query: {},
	query_add: function($div)
	{
		var data = $div.data();
		var Q = R.bn6draw._query;
		if (data.V in Q) {
			if (Q[data.V].includes(data.code)) return;
			else Q[data.V].push(data.code)
		} else {
			Q[data.V] = [data.code];
		}
		R.bnbrowser.query(Q);
	},
	query_del: function($div)
	{
		var data = $div.data();
		var Q = R.bn6draw._query;
		var i = Q[data.V].indexOf(data.code);
		if (i >= 0) Q[data.V].splice(i, 1);
		if (Q[data.V].length == 0) delete Q[data.V];
		R.bnbrowser.query(Q);
	},

	click: function(e)
	{
		var $div = $(e.target);
		var data = $div.data();
		var Q = R.bn6draw._query;

		$R.find("#bnb-clear").text("(clear)");

		if (data.selected) {
			data.selected = false;
			$div.removeClass("bnb-selected");
			R.bn6draw.query_del($div);
		} else {
			data.selected = true;
			$div.addClass("bnb-selected");
			R.bn6draw.query_add($div);
		}
	},

	/***********************/
	status_est: function(text) { $R.find("#bnb-status-est").text(text); },
	status_prob: function(text) { $R.find("#bnb-status-prob").text(text); },
	status_ips: function(text) { $R.find(".bnb-ips").text(text); },
};
