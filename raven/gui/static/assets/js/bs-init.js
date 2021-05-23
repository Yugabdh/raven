$(document).ready(function(){

	$('[data-bss-chart]').each(function(index, elem) {
		this.chart = new Chart($(elem), $(elem).data('bss-chart'));
	});

	$(document).ajaxStart(function() {
		$("img#loading-image").show();
	});
	
	$(document).ajaxComplete(function() {
		$("img#loading-image").hide();
	});
});