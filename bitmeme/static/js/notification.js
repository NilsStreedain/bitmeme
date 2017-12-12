$(document).ready(function(){
	$(".notification").height($(".noteText").outerHeight() - $(".noteSuf").outerHeight());
	$(".noteSuf").hide();
	$(".hideButton").click(function(){
	    $(".notification").hide();
	});
    $(".moreButton").click(function(){
        $(".notification").height($(".preNote").outerHeight() + $(".noteSuf").outerHeight() + 26);
		$(".noteSuf").show();
        $(".notification").height($(".preNote").outerHeight() + $(".noteSuf").outerHeight() + 26);
    });
});