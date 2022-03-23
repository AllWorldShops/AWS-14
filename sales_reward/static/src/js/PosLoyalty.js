//odoo.define('pos_loyalty.pos_loyalty', function (require) {
odoo.define('sales_reward.pos_loyalty', function (require) {
"use strict";

const { Context } = owl;
var BarcodeParser = require('barcodes.BarcodeParser');
var BarcodeReader = require('point_of_sale.BarcodeReader');
var PosDB = require('point_of_sale.DB');
var devices = require('point_of_sale.devices');
var concurrency = require('web.concurrency');
var config = require('web.config');
var core = require('web.core');
var field_utils = require('web.field_utils');
var time = require('web.time');
var utils = require('web.utils');
var AjaxService = require('web.AjaxService');
var rpc = require('web.rpc')
const { isRpcError } = require('point_of_sale.utils');

var QWeb = core.qweb;
var _t = core._t;
var Mutex = concurrency.Mutex;
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;

var exports = {};


var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');
const ObjNumberPopup = require('point_of_sale.NumberPopup');

var round_pr = utils.round_precision;

var _t = core._t;
var redeem_point=0;
var select_amount=0;
var type_of_customer = ''

models.load_fields('res.partner','total_points');
models.load_fields('res.partner','customer_type');
models.load_fields('pos.order','point_to_use','pos_point_to_use','total_pos_points','amount_into_points','amount_of_pos_point','customer_type_check','set_customer_type');

//models.load_models([
//    {
//    model: 'res.partner',
//    fields:['total_points','customer_type']
//    },
//],{'after': 'product.product'});


var _super = models.Order;
models.Order = models.Order.extend({

    redeem_points: function(){
        if (!this.get_client()) {
            return 0;
        }
        var client = this.get_client()
        var redeem = client.total_points
        return redeem;
    },
    get_won_points: function(){
//        var check_amount = this.set_redeem_point()
        if (!this.get_client()){
            return 0;
        }
        else{
//            if(check_amount !== 0){
//                var won_points = this.get_total_with_tax();
//            }
//            else{
//                var won_points = 0;
//            }
            var won_points = this.get_total_with_tax();
            return won_points;
        }
    },
    get_new_points: function() {
        if (!this.get_client()) {
            return 0;
        } else {
//            return round_pr(this.get_won_points() - this.get_spent_points(), 1);
//            return round_pr(this.get_won_points() - this.display_input_buffer(), 1);
            return round_pr(this.get_won_points(), 1);
        }
    },
    get_new_total_points: function() {
        if (!this.get_client()) {
            return 0;
        } else {
            if(this.state != 'paid'){
                return round_pr(this.get_client().total_points + this.get_new_points(), 1);
            }
            else{
                return round_pr(this.get_client().total_points, 1);
            }
        }
    },
    display_redeem_points: function() {

            if (this.get_client()) {
                var redeem = this.get_client().total_points;
            } else {
                var redeem = 0;
            }

            return redeem;
    },
    client_type:function(){
        var client = this.get_client();
        if(type_of_customer=='exp'){
            return false;
        }
        else{
            return true;
        }
    },
    display_input_buffer: function(){
        if (this.get_client()) {

//            var select_redeem = this.get_client().point_to_use;
            var select_redeem = this.get_client().pos_point_to_use;
        } else {
            var select_redeem = 0;
        }
        redeem_point = select_redeem

        return select_redeem;
    },

    show_redeem_point:function(){
        if (this.get('client')){
            var selected_point = this.get('client').point_to_use;
        }
        else {var selected_point = 0}
        return selected_point
    },

    calculate_amount:function(points){
        var fields={}
        var order = this.pos.get_order()
        this.pos.rpc({
                    model: 'res.partner',
                    method: 'get_redeem_price',
                    args: [[],[order]],
            }).then(function(values){
                if(values){
                var pos_amount = values['amount_per_point']
                select_amount = points * pos_amount
                }
            });
        return select_amount
    },
    set_redeem_point: function() {
        if (this.get_client()) {

//            var select_point = this.get_client().point_to_use;
            var select_point = this.get_client().pos_point_to_use;
            var fields={}
            var order = this.pos.get_order()
            var client = this.get_client()
           this.pos.rpc({
                model: 'res.partner',
                method: 'get_reward_amount',
                args: [[],[order]],
           }).then(function(values){
                sessionStorage.setItem('ind',values['ind']);
                sessionStorage.setItem('pro',values['pro']);
                sessionStorage.setItem('vip',values['vip']);
                sessionStorage.setItem('exp',values['exp']);
            });

           this.pos.rpc({
                model: 'pos.order',
                method: 'get_customer_type',
                args: [[],[client.id]],
           }).then(function(values){
                if(values){
                var type_customer = values
                type_of_customer = values
                }
           });

            if (select_point !== 0){
//                var amount_per_point = select_point * parseInt(sessionStorage.getItem(this.get_client().customer_type))
                var amount_per_point = select_point * parseInt(sessionStorage.getItem(client.customer_type))

                var select_redeem = amount_per_point
            }
            else{
                var select_redeem = 0;
            }
        }
        else {
            var select_redeem = 0;
        }
        select_amount = select_redeem;
        return select_redeem;
    },

    payable_amount: function() {

        var payable_amount = this.get_total_with_tax() - this.set_redeem_point();
        if(payable_amount > 0){
        }
        return payable_amount;
    },

    new_total: function() {
        return this.payable_amount();
    },

    get_total_with_tax: function() {
        var custom_redeem = round_pr(this.set_redeem_point(), this.pos.currency.rounding);
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_without_tax();
        }), 0) - custom_redeem, this.pos.currency.rounding);
    },

    custom_get_total_with_tax: function() {
        var custom_redeem = round_pr(this.set_redeem_point(), this.pos.currency.rounding);
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_without_tax();
        }), 0));
    },

    custom_get_total_without_tax: function() {
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_without_tax();
        }), 0), this.pos.currency.rounding);
    },

    export_as_JSON: function(){
        var data = _super.prototype.export_as_JSON.apply(this, arguments);
        data.point_to_use = redeem_point;
        data.amount_into_points = select_amount;
        return data;
    },
    finalize: function(){
        var client = this.get_client();
        if ( client ) {
//            client.total_points = this.get_new_total_points();
//            client.point_to_use = 0;
            location.reload()
            client.pos_point_to_use = 0;
        }
        _super.prototype.finalize.apply(this,arguments);
    }
});

});
