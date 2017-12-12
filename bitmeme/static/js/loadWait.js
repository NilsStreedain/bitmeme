$(document).ready(function() {
	$("#body > *").hide();
	$("#loadMsg").show();
});
$(window).load(function() {
	$("#body > *").show();
	$("#loadMsg").hide();
});