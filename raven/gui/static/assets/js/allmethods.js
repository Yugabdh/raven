function cms(data, tagid) {
	console.log(data)
	if (data.code == 200) {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th class="text-white">Categories</th> <th class="text-white">Name</th> </tr>');
		$.each(data.data, function (key, item) {
			$table.append('<tr><td> '+item.categories.join(", ")+ '</td><td> <a href="'+ item.url +'">'+item.name+'</a> </td></tr>');
		});

		$("#"+tagid).html($table)
	} else {
		$("#"+tagid).html('<tr><td colspan="2"> '+data.msg+ '</td></tr>');
	}
}

function dnsdumpster(data, tagid) {
	console.log(data)
	var as = {}
	if ("dns_records" in data) {
		$.each(data.dns_records.dns, function (key, item) {
			if (as[item.as]) {
				as[item.as] += 1
			} else {
				as[item.as] = 1
			}
		});
		$.each(data.dns_records.host, function (key, item) {
			if (as[item.as]) {
				as[item.as] += 1
			} else {
				as[item.as] = 1
			}
		});
		$.each(data.dns_records.mx, function (key, item) {
			if (as[item.as]) {
				as[item.as] += 1
			} else {
				as[item.as] = 1
			}
		});

		var values = $.map(as, function(value, key) { return value.toFixed(0) });
		var keys = $.map(as, function(value, key) { return key });
		var ctx = document.createElement('canvas');
		var config = {
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
		};

		new Chart(ctx, config);
		$div = $('<div>')
		$div.append(ctx);
		$("#"+tagid).html($div)

		$dns_table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$host_table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$mx_table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$txt_table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');

		if (data.dns_records.dns.length) {
			$("#"+tagid).append('<h5 class="py-3">DNS record</h5>')
			$dns_table.append('<tr><th class="text-white">Host Name</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr>')
			$.each(data.dns_records.dns, function (key, item) {
				$dns_table.append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
			});
			$("#"+tagid).append($dns_table)
		}

		if (data.dns_records.host.length) {
			$("#"+tagid).append('<h5 class="py-3">Host Table(A record)</h5>')
			$host_table.append('<tr><th class="text-white">Host</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr>')
			$.each(data.dns_records.host, function (key, item) {
				$host_table.append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
			});
			$("#"+tagid).append($host_table)
		}
		
		if (data.dns_records.mx.length) {
			$("#"+tagid).append('<h5 class="py-3">MX record</h5>')
			$mx_table.append('<tr><th class="text-white">Host</th> <th class="text-white">IP</th> <th class="text-white">AS</th></tr>')
			$.each(data.dns_records.mx, function (key, item) {
				$mx_table.append('<tr><td> '+item.domain+ '<br />'+item.header+'</td><td>'+item.ip+'<br />'+item.reverse_dns+'</td><td>'+item.as+'</td></tr>');
			});
			$("#"+tagid).append($mx_table);
		}
		
		if (data.dns_records.txt.length) {
			$("#"+tagid).append('<h5 class="py-3">TXT record Sender Policy Framework (SPF) configurations</h5>')
			$.each(data.dns_records.txt, function (key, item) {
				$txt_table.append('<tr><td> '+item+'</td></tr>');
			});
			$("#"+tagid).append($txt_table);
		}		

		$("#"+tagid).append('<h5 class="py-3">The map</h5>')
		$("#"+tagid).append('<a href="'+data.image_url+'" target="_blank"> Click here <3</a>')
	} else {
		$("#"+tagid).html('<p class="py-3">Error no records found on dnsdumpster.com</h5>')
	}
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
	hs.properties.fill = am4core.color("#1e1e1e");

	// Remove Antarctica
	polygonSeries.exclude = ["AQ"];

	// Create image series
	var imageSeries = chart.series.push(new am4maps.MapImageSeries());

	// Create a circle image in image series template so it gets replicated to all new images
	var imageSeriesTemplate = imageSeries.mapImages.template;
	var circle = imageSeriesTemplate.createChild(am4core.Circle);
	circle.radius = 4;
	circle.fill = am4core.color("#975aff");
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
	if (!$.isEmptyObject(data)){
		$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$table.append('<tr><th class="text-white">'+name+'</th></tr>');
		$tr = $('<tr>');
		$td = document.createElement('td');
		if (name === "Ipstack") {
			pointOnmap($td, data.latitude, data.longitude, data.city);
		} 
		
		else if (name === "Ipinfo") {
			var location = data.loc.split(",")
			pointOnmap($td, parseFloat(location[0]), parseFloat(location[1]), data.city);
		} 
		
		else if (name === "Hackertarget") {
			pointOnmap($td, parseFloat(data.Latitude), parseFloat(data.Longitude), data.City);
		}
		$tr.append($td);
		$table.append($tr)
		var str = JSON.stringify(data, undefined, 4)
		$table.append('<tr><td><pre>'+syntaxHighlight(str)+'</pre></td></tr>');
		$("#"+tagid).html($table)
	} else {
		$("#"+tagid).html("<p class='pb-3'>Error occured</p>")
	}
}

function googledork(data, tagid, dork) {
	console.log(result)
	if(dork === undefined) {
		dork = "''";
	} 
	$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
	$table.append('<tr><th class="text-white">URLs found for dork: '+dork+'</th></tr>');
	if(data.length) {
		$td = $('<td>')
		$.each(data, function (key, item) {
			$td.append('<a href="'+item+'" target="_blank">'+item+'</a><br />');
		});
		$table.append($td);
		$("#"+tagid).append($table)
		console.log(data)
	} else {
		$table.append('<tr><td>None</td></tr>');
	}
}

function reverseip(data, tagid, name) {
	console.log(data)
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th class="text-white">'+name+'</th></tr>');
	if (data.length) {
		$tr = $('<tr>');
		$td = $('<td>');
		$.each(data, function (key, item) {
			$td.append(item+'<br />');
		});
		$tr.append($td);
		$table.append($tr);
		$("#"+tagid).append($table);
	} else {
		$table.append('<tr><td>No results found!</td></tr>');
	}
}

function subdomain(data, tagid, name) {
	console.log(data)
	$table = $('<table class="table table-bordered py-2">');
	if (data.length) {
		$table.append('<tr><th class="text-white">Output with ' + name + '</th></tr>');
		$tr = $('<tr>')
		$td = $('<td>')
		$.each(data, function (key, item) {
			$td.append(item+'<br />');
		});
		$tr.append($td)
		$table.append($tr)
	} else {
		$table.append('<tr><td>No subdomain found!</td></tr>');
	}
	$("#"+tagid).append($table)
}

function wayback(data, tagid) {
	console.log(data)
	$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
	$table.append('<tr><th class="text-white">original</th><th class="text-white">timestamp</th><th class="text-white">endtimestamp</th><th class="text-white">groupcount</th><th class="text-white">uniqcount</th></tr>');
	$.each(data.slice(1,), function (key, item) {
		var timestamp = item[1].slice(0, 4)+"-"+item[1].slice(4, 6)+"-"+item[1].slice(6, 8)+"-"+item[1].slice(8, 10)+"-"+item[1].slice(10, 12)+"-"+item[1].slice(12, 14);
		var endtimestamp = item[2].slice(0, 4)+"-"+item[2].slice(4, 6)+"-"+item[2].slice(6, 8)+"-"+item[2].slice(8, 10)+"-"+item[2].slice(10, 12)+"-"+item[2].slice(12, 14);
		$table.append('<tr><td>'+item[0]+'</td><td>'+timestamp+'</td><td>'+endtimestamp+'</td><td>'+item[3]+'</td><td>'+item[4]+'</td></tr>');
	});
	$("#"+tagid).append($table)
}

function whois(data, tagid, name) {
	if (name === "whois") {
		$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$table.append('<tr><th class="text-white">'+name+'</th></tr>');
		$table.append('<tr><td style="white-space:pre-wrap;">'+data+'</td></tr>');

		$("#"+tagid).append($table)
	}
	
	else if (name === "ipwhois") {
		$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
		$table.append('<tr><th class="text-white">'+name+'</th></tr>');
		var str = JSON.stringify(data, undefined, 4)
		$table.append('<tr><td><pre>'+syntaxHighlight(str)+'</pre></td></tr>');
		$("#"+tagid).append($table)
	}
	console.log(data)
}

function traceroute_map(locations, points, div) {
	var chart = am4core.create(div, am4maps.MapChart);

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
	hs.properties.fill = am4core.color("#1e1e1e");

	// Remove Antarctica
	polygonSeries.exclude = ["AQ"];

	// Add line series
	var lineSeries = chart.series.push(new am4maps.MapLineSeries());
	lineSeries.mapLines.template.nonScalingStroke = true;
	lineSeries.mapLines.template.strokeWidth = 3;
	lineSeries.mapLines.template.stroke = am4core.color("#975aff");
	lineSeries.data = [{
	"multiGeoLine": [
		locations
	]
	}];

	// Create image series
	var imageSeries = chart.series.push(new am4maps.MapImageSeries());

	// Create a circle image in image series template so it gets replicated to all new images
	var imageSeriesTemplate = imageSeries.mapImages.template;
	var circle = imageSeriesTemplate.createChild(am4core.Circle);
	circle.radius = 4;
	circle.fill = am4core.color("#975aff");
	circle.stroke = am4core.color("#FFFFFF");
	circle.strokeWidth = 2;
	circle.nonScaling = true;
	circle.tooltipText = "{title}";

	// Set property fields
	imageSeriesTemplate.propertyFields.latitude = "latitude";
	imageSeriesTemplate.propertyFields.longitude = "longitude";

	// Add data for the three cities
	imageSeries.data = points;
}

function traceroute(data, tagid) {
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th>Traceroute</th></tr>');
	var locations = [];
	var points = [];
	$.each(data, function (key, item) {
		locations.push({"latitude":item.latitude, "longitude":item.longitude})
		points.push({"latitude":item.latitude, "longitude":item.longitude, "title": item.ip})
	});
	$tr = $('<tr>')
	$td = document.createElement('td');
	traceroute_map(locations, points, $td)
	$tr.append($td)
	$table.append($tr)
	var str = JSON.stringify(data, undefined, 4)
	$table.append('<tr><td><pre>'+syntaxHighlight(str)+'</pre></td></tr>');
	$("#"+tagid).append($table)
	console.log(data)
}

function buildwith(data, tagid) {
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th>For</th><th>BuildWith</th></tr>');
	$.each(data, function (key, item) {
		$table.append('<tr><td>'+key+'</td><td>'+item.join(", ")+'</td></tr>');
	});
	$("#"+tagid).append($table);
	console.log(data)
}

function robot(data, tagid, name) {
	if (name === "robot") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>robots.txt</th></tr>');
		$table.append('<tr><th>Disallowed</th></tr>');
		$.each(data.Disallowed, function (key, item) {
			$table.append('<tr><td>'+item+'</td></tr>');
		});
		$table.append('<tr><th>Allowed</th></tr>');
		$.each(data.Allowed, function (key, item) {
			$table.append('<tr><td>'+item+'</td></tr>');
		});
		$("#"+tagid).append($table);
		console.log("robot")
	}
	if (name === "sitemap") {
		$table = $('<table class="table table-bordered py-2">');
		$table.append('<tr><th>sitemap.xml</th></tr>');
		json = data.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
		$table.append('<tr><td><pre style="white-space:pre-wrap;">'+json+'</pre></td></tr>');
		$("#"+tagid).append($table);
		console.log("sitemap")
	}
	console.log(data)
}

function sslinfo(data, tagid) {
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th></th><th>Data</th></tr>');
	$.each(data, function (key, item) {
		if (key === "certRaw") {
			var str = JSON.stringify(data, undefined, 4);
			$table.append('<tr><td>'+key+'</td><td><pre>'+syntaxHighlight(str)+'</pre></td></tr>');
		} else {
			$table.append('<tr><td>'+key+'</td><td>'+item+'</td></tr>');
		}
		
	});
	$("#"+tagid).append($table);
	console.log(data)
}

function osmapping(data, tagid) {
	console.log(data)
	if (data.error) {
		$("#"+tagid).append('<div> <p class="text-danger">'+data.msg+'</p> </div>')
	}
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th colspan="2">OS Match</th></tr>');
	$tr = $('<tr>')
	$td_graph = $('<td colspan="2">')
	var os_name = [];
	var accuracy = [];
	var ip = Object.keys(data)[0]
	$.each(data[ip].osmatch, function (key, item) {
		os_name.push(item.name);
		accuracy.push(item.accuracy);
	});
	var ctx = document.createElement('canvas');
	var config = {
		type: 'line',
		data: {
			labels: os_name,
			datasets: [{
					label: "OS Accuracy",
					data: accuracy,
					fill: false,
					borderColor: "#975aff",
					tension: 0.1
				}]
		},
		options: {
			responsive: true,
			legend: {
				position: 'bottom',
			},
			hover: {
				mode: 'label'
			},
			scales: {
				xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'OS Name'
						}
					}],
				yAxes: [{
						display: true,
						ticks: {
							beginAtZero: true,
							steps: 10,
							stepValue: 10,
							max: 100
						}
					}]
			}
		}
	};
	new Chart(ctx, config);
	$td_graph.append(ctx);
	$tr.append($td_graph);
	$table.append($tr)
	
	$.each(data[ip].osmatch, function (key, item) {
		$tr = $('<tr>')
		$td_os_name = $('<td>')
		$td_data = $('<td>')
		$td_os_name.append(item.name)
		var str = JSON.stringify(item, undefined, 4);
		$td_data.append('<pre>'+syntaxHighlight(str)+'</pre>')
		$tr.append($td_os_name)
		$tr.append($td_data)
		$table.append($tr)
	});
	$("#"+tagid).append($table)
}

function webserver(data, tagid) {
	console.log(data)

	$table = $('<table class="table table-bordered py-2" style="table-layout: fixed">');
	if (data.Server) {
		$table.append('<tr><td>Server</td><td>'+data.Server+'</td><tr>')
	}
	var str = JSON.stringify(data.raw, undefined, 4);
	$table.append('<tr><td>Raw Header</td><td><pre>'+syntaxHighlight(str)+'</pre></td><tr>')
	$("#"+tagid).append($table)
}

function portscan(data, tagid) {
	console.log(data)
	if (data.error) {
		$("#"+tagid).append('<div> <p class="text-danger">'+data.msg+'</p> </div>')
	}
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th colspan="5">Well known ports scan</th></tr>');
	$table.append('<tr><th>Port</th><th>Protocol</th><th>Reason</th><th>Status</th><th>Service</th></tr>');
	var ip = Object.keys(data)[0]
	$.each(data[ip].ports, function (key, item) {
		$table.append('<tr><td>'+item.portid+'</td><td>'+item.protocol+'</td><td>'+item.reason+'</td><td>'+item.state+'</td><td>'+item.service.name+'</td></tr>');
	});
	$("#"+tagid).append($table)
}


function subnet(data, tagid) {
	console.log(data)
	if (data.error) {
		$("#"+tagid).append('<div> <p class="text-danger">'+data.msg+'</p> </div>')
	}
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th>'+data.runtime.summary+'</th></tr>');
	$.each(data, function (key, item) {
		if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(key))
		{
			$table.append('<tr><td>'+key+'</td></tr>');
		}
	});
	$("#"+tagid).append($table)
}

function pingscan(data, tagid) {
	console.log(data)
	if (data.error) {
		$("#"+tagid).append('<div> <p class="text-danger">'+data.msg+'</p> </div>')
	}
	$table = $('<table class="table table-bordered py-2">');
	$.each(data, function (key, item) {
		$table.append('<tr><td>'+item.hostname+'</td><td>'+item.address+'</td></tr>');
	});
	$("#"+tagid).append($table)
}

function dnsbrute(data, tagid) {
	console.log(data)
	if (data.error) {
		$("#"+tagid).append('<div> <p class="text-danger">'+data.msg+'</p> </div>')
	}
	$table = $('<table class="table table-bordered py-2">');
	$table.append('<tr><th>Hostname</th><th>IP address</th></tr>');
	$.each(data, function (key, item) {
		$table.append('<tr><td>'+item.hostname+'</td><td>'+item.address+'</td></tr>');
	});
	$("#"+tagid).append($table)
}
