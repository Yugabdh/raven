function cms(data) {
	console.log(data)
	if (data.code == 200) {
		$('#output').append('<tr><th class="text-white">Categories</th> <th class="text-white">Name</th> </tr>')
		$.each(data.data, function (key, item) {
			$('#output').append('<tr><td> '+item.categories.join(", ")+ '</td><td> <a href="'+ item.url +'">'+item.name+'</a> </td></tr>');
		});
	} else {
		$('#output').append('<tr><td colspan="2"> '+data.msg+ '</td></tr>');
	}
}

function dnsdumpster(data, tagid) {
	console.log(data)
	$("#"+tagid).append('<div> <canvas id="dnsdumster'+tagid+'"></canvas> </div>')

	var ctx = document.getElementById('dnsdumster'+tagid);
	var as = {}
	$("#"+tagid).append('<h5 class="py-3">DNS record</h5>')
	$("#"+tagid).append('<table class="table table-bordered"><tr><th class="text-white">Host Name</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr></table>')
	$.each(data.dns_records.dns, function (key, item) {
		if (as[item.as]) {
			as[item.as] += 1
		} else {
			as[item.as] = 1
		}
		$("#"+tagid+" table").append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
	});
	$("#"+tagid).append('<h5 class="py-3">Host Table(A record)</h5>')
	$("#"+tagid).append('<table class="table table-bordered"><tr><th class="text-white">Host</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr></table>')
	$.each(data.dns_records.host, function (key, item) {
		if (as[item.as]) {
			as[item.as] += 1
		} else {
			as[item.as] = 1
		}
		$("#"+tagid+" table:nth-child(5)").append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
	});
	$("#"+tagid).append('<h5 class="py-3">MX record</h5>')
	$("#"+tagid).append('<table class="table table-bordered"><tr><th class="text-white">Host</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr></table>')
	$.each(data.dns_records.mx, function (key, item) {
		if (as[item.as]) {
			as[item.as] += 1
		} else {
			as[item.as] = 1
		}
		$("#"+tagid+" table:nth-child(7)").append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
	});
	$("#"+tagid).append('<h5 class="py-3">TXT record Sender Policy Framework (SPF) configurations</h5>')
	$("#"+tagid).append('<table class="table table-bordered"></table>')
	$.each(data.dns_records.txt, function (key, item) {
		$("#"+tagid+" table:nth-child(9)").append('<tr><td> '+item+'</td></tr>');
	});
	$("#"+tagid).append('<h5 class="py-3">The map</h5>')
	$("#"+tagid).append('<a href="'+data.image_url+'" target="_blank"> Click here <3</a>')
	var values = $.map(as, function(value, key) { return value.toFixed(0) });
	var keys = $.map(as, function(value, key) { return key });
	var myChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: keys,
			datasets: [{
				label: 'Hosting (IP block owners)',
				data: values,
				borderWidth: 1,
				backgroundColor: palette('cb-BuGn', keys.length).map(function(hex) {
					return '#' + hex;
				})
			}]
		},
		options: {
			scales: {
				y: {
					beginAtZero: true,
					min: 0,
				}
			}
		}
	});
}

function pointOnmap(divid, latitude, longitude, city) {
	var chart = am4core.create(divid, am4maps.MapChart);
	// Set map definition
	chart.geodata = am4geodata_worldLow;

	// Set projection
	chart.projection = new am4maps.projections.Miller();

	// Create map polygon series
	var polygonSeries = chart.series.push(new am4maps.MapPolygonSeries());

	// Make map load polygon (like country names) data from GeoJSON
	polygonSeries.useGeodata = true;

	// Configure series
	var polygonTemplate = polygonSeries.mapPolygons.template;
	polygonTemplate.tooltipText = "{name}";
	polygonTemplate.fill = am4core.color("#74B266");

	// Create hover state and set alternative fill color
	var hs = polygonTemplate.states.create("hover");
	hs.properties.fill = am4core.color("#367B25");

	// Remove Antarctica
	polygonSeries.exclude = ["AQ"];

	// Create image series
	var imageSeries = chart.series.push(new am4maps.MapImageSeries());

	// Create a circle image in image series template so it gets replicated to all new images
	var imageSeriesTemplate = imageSeries.mapImages.template;
	var circle = imageSeriesTemplate.createChild(am4core.Circle);
	circle.radius = 4;
	circle.fill = am4core.color("#B27799");
	circle.stroke = am4core.color("#FFFFFF");
	circle.strokeWidth = 2;
	circle.nonScaling = true;
	circle.tooltipText = "{title}";

	// Set property fields
	imageSeriesTemplate.propertyFields.latitude = "latitude";
	imageSeriesTemplate.propertyFields.longitude = "longitude";

	// Add data for the three cities
	imageSeries.data = [{
		"latitude": latitude,
		"longitude": longitude,
		"title": city
	}];
}

function output(inp, obj) {
	document.getElementById(inp).appendChild(document.createElement('pre')).innerHTML = obj;
}

function syntaxHighlight(json) {
	json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
		var cls = 'number';
		if (/^"/.test(match)) {
			if (/:$/.test(match)) {
				cls = 'key';
			} else {
				cls = 'string';
			}
		} else if (/true|false/.test(match)) {
			cls = 'boolean';
		} else if (/null/.test(match)) {
			cls = 'null';
		}
		return '<span class="' + cls + '">' + match + '</span>';
	});
}

function geoip(data, tagid, name) {
	if (name === "Ipstack") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="Ipstackmap"></td></tr>');
		$table.append('<tr><td id="Ipstackdata"></td></tr>');

		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('Ipstackdata', syntaxHighlight(str));
		pointOnmap("Ipstackmap", data.latitude, data.longitude, data.city)
	} 
	
	else if (name === "Ipinfo") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="Ipinfomap"></td></tr>');
		$table.append('<tr><td id="Ipinfodata"></td></tr>');
		
		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('Ipinfodata', syntaxHighlight(str));
		var location = data.loc.split(",")
		pointOnmap("Ipinfomap", parseFloat(location[0]), parseFloat(location[1]), data.city)
	} 
	
	else if (name === "Hackertarget") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="Hackertargetmap"></td></tr>');
		$table.append('<tr><td id="Hackertargetdata"></td></tr>');
		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('Hackertargetdata', syntaxHighlight(str));
		pointOnmap("Hackertargetmap", parseFloat(data.Latitude), parseFloat(data.Longitude), data.City)
	} 
	console.log(data)
}

function googledork(data, tagid, dork) {
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th>URLs found for dork: '+dork+'</th></tr>');
	var result = data.join("<br />");
	console.log(result)
	$table.append('<tr><td>'+result+'</td></tr>');
	$("#"+tagid).append($table)
	console.log(data)
}

function reverseip(data, tagid, name) {
	if (name === "yougetsignal") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="yougetsignaldata_reverseip"></td></tr>');

		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('yougetsignaldata_reverseip', syntaxHighlight(str));
	}
	
	else if (name === "Hackertarget") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="Hackertargetdata_reverseip"></td></tr>');
		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('Hackertargetdata_reverseip', syntaxHighlight(str));
	} 
	console.log(data)
}

function subdomain(data, tagid, name) {
	$table = $('<table class="table table-bordered py-2">');
	if (name === "dnsdumpster") {
		$table.append('<tr><th>Output with DNS dumpster</th></tr>');
		$table.append('<tr><td id="subdomain_dnsdumpster_data"></td></tr>');
		$("#"+tagid).append($table)
		$.each(data, function (key, item) {
			$("#subdomain_dnsdumpster_data").append(item+'<br />');
		});
	}
	if (name === "google_dork") {
		$table.append('<tr><th>Output with Google Dork</th></tr>');
		$table.append('<tr><td id="subdomain_google_data"></td></tr>');
		$("#"+tagid).append($table)
		$.each(data, function (key, item) {
			$("#subdomain_google_data").append(item+'<br />');
		});
	}
	console.log(data)
}

function wayback(data, tagid) {
	$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
	$table.append('<tr><th>original</th><th>mimetype</th><th>timestamp</th><th>endtimestamp</th><th>groupcount</th><th>uniqcount</th></tr>');
	$.each(data.slice(1,), function (key, item) {
		var timestamp = new Date(parseInt(item[2]));
		var endtimestamp = new Date(parseInt(item[3]));
		$table.append('<tr><td>'+item[0]+'</td><td>'+item[1]+'</td><td>'+timestamp.toISOString()+'</td><td>'+endtimestamp.toISOString()+'</td><td>'+item[4]+'</td><td>'+item[5]+'</td></tr>');
	});
	$("#"+tagid).append($table)
	console.log(data)
}

function whois(data, tagid, name) {
	if (name === "whois") {
		$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="whoisdata" style="white-space:pre-wrap;">'+data+'</td></tr>');

		$("#"+tagid).append($table)
	}
	
	else if (name === "ipwhois") {
		$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$table.append('<tr><th>'+name+'</th></tr>');
		$table.append('<tr><td id="ipwhoisdata"></td></tr>');
		$("#"+tagid).append($table)
		var str = JSON.stringify(data, undefined, 4)
		output('ipwhoisdata', syntaxHighlight(str));
	}
	console.log(data)
}

$(document).ajaxStart(function() {
    $("img#loading-image").show();
});

$(document).ajaxComplete(function() {
    $("img#loading-image").hide();
});