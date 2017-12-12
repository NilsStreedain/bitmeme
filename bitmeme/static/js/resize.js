$(window).on('resize', function(event){
    var windowWidth = $(window).width();
	if(windowWidth > 650){
   		nav.style.display = 'block';
	} else {
		nav.style.display = 'none';
	}
});