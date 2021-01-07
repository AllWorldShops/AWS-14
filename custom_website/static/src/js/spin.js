$(document).ready(function() {
	
	$('#delivery_carrier').find('.list-group li').first().find('i').removeClass("spinner_hide");

	$("input").click(function() {
		$(this).parent().find('i').removeClass("spinner_hide");
	});
});
