odoo.define('emipro_theme_base.category_wise_search', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var productsSearchBar = publicWidget.registry.productsSearchBar

    productsSearchBar.include({
        events: _.extend({}, productsSearchBar.prototype.events, {
            //'change .ept-parent-category': '_onInput',
            'change .ept-parent-category': 'change_category',
            'change .ept-brand-category': 'change_brand',
        }),
        
        change_category: function() {
        
        	this.get_brands();
        	
            if (this.$input.val()){
                this._onInput();
            }
        },
        
        get_brands: function() {
        		$.ajax({
	            url: "/shop/category/brands/custom",
	            type: 'POST',
	            async: false,
	            data: {
	                'cat_id':this.$('.ept-parent-category:visible option:selected').val(),
	            },
	            success: function (result) {
	                var resultJSON = jQuery.parseJSON(result);
	                //alert(resultJSON);
                    $('.ept-brand-category').empty();
                    
                    //$('.therapist-location-list').append(`
					//	<option value="" disabled="disabled" selected="selected">Choose Therapist</option>
                    //`);

	                $.each(resultJSON, function (key, value) {
	                    $('.ept-brand-category').append(`
							
							<option class="o_default_snippet_text" value="`+ value['id']+`">`+ value['name'] +`</option>
                                
                         `);
                                 
		                });
		
		            },
		     });
        	
        },
        
        
        change_brand: function() {
            if (this.$input.val()){
                this._onInput();
            }
        },
        
        
        
        
        
        
        
        _fetch: function () {
            /*var val ={
                'term' : this.$input.val(),
                'cat_id' : this.$('.ept-parent-category:visible option:selected').val()
            }*/
            return this._rpc({
                route: '/shop/products/autocomplete/custom',
                params: {
                    'term': this.$input.val(),
                    'options': {
                        'order': this.order,
                        'limit': this.limit,
                        'display_description': this.displayDescription,
                        'display_price': this.displayPrice,
                        'max_nb_chars': Math.round(Math.max(this.autocompleteMinWidth, parseInt(this.$el.width())) * 0.22),
                        'cat_id' : this.$('.ept-parent-category:visible option:selected').val(),
                        'brand_id' : this.$('.ept-brand-category:visible option:selected').val()
                    },
                },
            });
        },
    });
});
