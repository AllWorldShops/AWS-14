odoo.define('sales_reward.VariantMixinInherit', function (require) {
'use strict';

var concurrency = require('web.concurrency');
var core = require('web.core');
var utils = require('web.utils');
var ajax = require('web.ajax');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
console.log(VariantMixin);
VariantMixin.onClickAddCartJSON = function(ev){

        ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.input-group').find("input");
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

            var product_id = {'product_id':$input.attr('data-product-id')}
            return ajax.rpc("/product/confirmation", {product_id}).then(function(data){
                if(data){

                    $input.prop( "disabled", true );
                    return false;

                }
                else{
                     if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
                }
            });
            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
            return false;
    };
});
