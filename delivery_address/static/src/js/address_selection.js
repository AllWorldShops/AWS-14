
$(document).ready(function(){

	if($('.t_signin').html() == undefined || $('.t_signin').html() == ''){
		$(".login_button_div").addClass("button_hide");
	}
	else{
		$(".login_button_div").removeClass("button_hide");
	}	

	$(".delivery_address_button").click(function(){
		
		$('.add_current_url_val').val(window.location.href);
		var newAttr = $('#create_delivery_address').attr('href') + '?url=' + window.location.pathname.split( '/' );
		$('#create_delivery_address').attr('href', newAttr);
	});
	
	
	if($('.t_signin').html() == undefined || $('.t_signin').html() == ''){
		$(".login_add_address_button_div").removeClass("button_hide");
	}
	else{
		$(".login_add_address_button_div").addClass("button_hide");
	}		


	


	$("#submit").click(function() {
	   window.location.reload();
		});
	
	$('.btn-ship-delviery').click(function() {
		var ship_id = $(this).attr("data-ship_id");
		$.ajax({     
		 	url: '/update_delviery_address',
            type: 'POST',
            data:{ship_id:ship_id},
            success: function(response){
            	 window.location.reload();
            
            }
		});
	});
});

