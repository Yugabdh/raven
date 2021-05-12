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

function dnsdumpster(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}

function geoip(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}

function googledork(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}

function reverseip(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}

function wayback(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}

function whois(data) {
	$('#output').text('<p> TODO</p>');
	console.log(data)
}