// ==UserScript==
// @name           fix-autoreg-client-links
// @namespace      http://seas.harvard.edu/ns/greasemonkey/
// @include        https://autoreg.fas.harvard.edu/tools/*
// ==/UserScript==

CLIENT_URL = 'https://autoreg.fas.harvard.edu/tools/client/client.html?macAddress='

// These are just examples of the data we're dealing with.
// <a href="javascript:_client('00:50:56:88:25:10')">00:50:56:88:25:10</a>
// <a href="javascript:_detail('00:50:56:88:25:10')">00:50:56:88:25:10</a>
// POSTDATA=macAddress=c0%3Aff%3Aee%3Aac%3A01%3Aa0&previousPage=%2Ftools%2Fscopes.html&scope=140.247.51.0&metricsUrl=

// Replace javascript:_client and javascript:_detail links with
// a corresponding href.
function replace_javascript_links() {
	var candidates = document.getElementsByTagName("a");
	for (var cand = null, i = 0; (cand = candidates[i]); i++) {
		var macaddr;

		if (cand.href.toLowerCase().indexOf("javascript:_client") == 0) { 
			macaddr = cand.href.substr(20, 17)
		}  else if (cand.href.toLowerCase().indexOf("javascript:_detail") == 0) {
			macaddr = cand.href.substr(20, 17)
		}

		if (macaddr)
			cand.href = CLIENT_URL + macaddr
	}
}


// Replace bare MAC addresses in table cells with appropriate
// client links.
function replace_mac_addrs () {
	var candidates = document.getElementsByTagName("td");
	macaddrRegex = /([0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f])/i;
	for (var cand = null, i = 0; (cand = candidates[i]); i++) {
		if (! cand.getAttribute('class') == 'cell')
			continue;

		text = cand.firstChild.textContent;
		var match = cand.firstChild.textContent.match(macaddrRegex);
		if (! match) {
			if (text.indexOf('00:') == 0)
				alert("Failed to match: " + text);
			continue;
		}

		var a = document.createElement("a");
		a.setAttribute('href', CLIENT_URL + match[0]);
		a.appendChild(document.createTextNode(match[0]));
		cand.replaceChild(a, cand.firstChild);
	}
}

function display_indicator () {
	var div = document.createElement("div");
	div.style.border = "thin solid black";
	div.style.background = "yellow";
	div.appendChild(document.createTextNode("Fixed client links."));

	document.body.insertBefore(div, document.body.firstChild);
}

replace_javascript_links();
replace_mac_addrs();
display_indicator();

