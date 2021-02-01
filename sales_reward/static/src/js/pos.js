odoo.define('sales_reward.reward', function(require) {
"use strict";
    var rpc = require('web.rpc');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;
    var round_pr = utils.round_precision;
    var QWeb = core.qweb;
    var _super_order = models.Order;
    // models.load_fields('res.partner', ['total_pos_points','remaining_points','is_pos_user']);
    models.load_fields('res.partner', ['total_points','remaining_points','is_pos_user','customer_type']);
    models.load_fields('pos.order', ['total_pos_points', 'point_to_use','amount_into_points','customer_type_check']);
    var _super_order = models.Order;
    var redeem_point=0;
    var select_amount=0;

    screens.ClientListScreenWidget.include({
        render_list: function(partners){
        var contents = this.$el[0].querySelector('.client-list-contents');
        contents.innerHTML = "";
        for(var i = 0, len = Math.min(partners.length,1000); i < len; i++){
            if (partners[i]["is_pos_user"]===true){
                var partner    = partners[i];
                var clientline = this.partner_cache.get_node(partner.id);
                if(!clientline){
                    var clientline_html = QWeb.render('ClientLine',{widget: this, partner:partners[i]});
                    var clientline = document.createElement('tbody');
                    clientline.innerHTML = clientline_html;
                    clientline = clientline.childNodes[1];
                    this.partner_cache.cache_node(partner.id,clientline);
                }
                if( partner === this.old_client ){
                    clientline.classList.add('highlight');
                }else{
                    clientline.classList.remove('highlight');
                }
                contents.appendChild(clientline);   
            }
        }
    },

    });
    // Custom widget
    var CustomPopupWidget = PopupWidget.extend({
        template: 'CustomPopupWidget',
        show: function(options){
            options = options || {};
            this._super(options);
            this.inputbuffer = '' + (options.value   || '');
            this.decimal_separator = _t.database.parameters.decimal_point;
            this.renderElement();
            this.firstinput = true;
        },
        click_numpad: function(event){

            var newbuf = this.gui.numpad_input(
                this.inputbuffer, 
                $(event.target).data('action'), 
                {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);
           
            if (newbuf !== this.inputbuffer) {
                this.inputbuffer = newbuf;
                this.$('.value').text(this.inputbuffer);

            }
        },
        renderElement: function(){
            try{
            this._super()}
            catch(err){console.error(err.message, err.stack);}
            this.$('.popup').addClass('popup-customtextinput');
        },
        click_confirm: function(){
            debugger
            this.gui.close_popup();
            if( this.options.confirm ){
                redeem_point = this.inputbuffer;
                this.options.confirm.call(this,this.inputbuffer);
            }
            return redeem_point;
        },
      
    });
    gui.define_popup({name:'customtextinput', widget: CustomPopupWidget});

var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            this.on('change:client', function(){
                var client = this.get_client();
              
            }, this);
            return _super_order.initialize.apply(this, arguments);
        },
        
        client_type:function(){
            var client = this.get_client();
            if(client.customer_type=='exp'){
                return false;
            }
            else{
                return true;

            }
        },
        display_redeem_points: function() {

          
            if (this.get('client')) {
               
                // var redeem = this.get('client').total_pos_points;
                var redeem = this.get('client').total_points;
                console.log('Hellllllllllloooooooooooooooooo');
                
            } else {
                var redeem = 0;
            }
            console.log('display redeem');//20
            console.log(redeem);

     
            return redeem;
        },
        display_input_buffer: function(){
            if (this.get('client')) {
               
                this.get('client').point_to_use = redeem_point;
            
                var select_redeem = this.get('client').point_to_use;
            } else {
                var select_redeem = 0;
            }
            console.log('display_input_buffer');//20
            console.log(select_redeem);
            
            return select_redeem;

        },
        show_redeem_point:function(){
            if (this.get('client')){
                var selected_point = this.get('client').point_to_use;
            }
            else {var selected_point = 0}
            console.log('show_redeem_point');//2
            console.log(selected_point);
            return selected_point


        },

        set_redeem_point: function() {

            if (this.get('client')) {
                var select_point = this.get('client').point_to_use
                if (select_point){

                    var amount=this.calculate_amount(select_point)
                    var select_redeem=amount
                }
            } 
            else {
                var select_redeem = 0;
            }
            console.log('set_redeem_point');//1.5
            console.log(select_redeem);

            var select_point=0;
            return select_redeem;
        },
        // calculate_amount:function(points){
        //     var fields={}

        //     var order = this.pos.get_order()
        //     rpc.query({
        //                 model: 'res.partner',
        //                 method: 'get_setting_values',
        //                 args: [fields],
        //             })
        //             .then(function(values){
                 
        //             // if (values['is_pos_reward']){
        //             if (values['ind_amount_per_point']){
        //                // if(values['pos_amount_per_point']){
        //                 if(values['ind_amount_per_point']){
        //                 var pos_amount=values['ind_amount_per_point']
        //                 select_amount=points*pos_amount
                      
        //                }
        //                 else{
        //                     select_amount=0}
        //             }
        //             else { select_amount=0
        //              }  
        //             });
        //             return select_amount
        // },
        calculate_amount:function(points){
            var fields={}

            var order = this.pos.get_order()
            rpc.query({
                        model: 'res.partner',
                        method: 'get_redeem_price',
                        args: [[],[order]],
                    })
                    .then(function(values){
                        var pos_amount = values['amount_per_point']
                        select_amount = points*pos_amount
                    });
                    console.log('calculate_amount');//1.5
                    console.log(select_amount);

                    return select_amount
        },

        payable_amount: function() {
            
            var payable_amount = this.get_total_with_tax() - this.set_redeem_point();
            if(payable_amount > 0){
            }
            console.log('payable_amount');
            console.log(payable_amount);

            return payable_amount;
        },
        new_total: function() {
            return this.payable_amount();
        },
        get_total_without_tax: function() {
            var custom_redeem = round_pr(this.set_redeem_point(), this.pos.currency.rounding);

            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0) - custom_redeem, this.pos.currency.rounding);
        },
        custom_get_total_without_tax: function() {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        },

        
        export_as_JSON: function(){
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.point_to_use=redeem_point;
            data.amount_into_points="100";
            // data.amount_into_points=select_redeem;
            // data.amount_into_points=select_amount
            console.log(data);
            return data;
        }
});
       //Screen-Display-------------------------------------------------------------------------------
    screens.PaymentScreenWidget.include({
             customer_changed: function(){
                    var client = this.pos.get_client();
                    this.$('.js_customer_name').text( client ? client.name : _t('Customer') );
                    if(client){
                        if(client.customer_type=='exp'){
                            $("#check").hide();
                          }
                        else{
                             $("#check").show();
                            }     
                    }
                },
        render_paymentlines: function() {
            var self = this;
            var order = this.pos.get_order();
            if (!order) {
                return;
            }
            var lines = order.get_paymentlines();
            var due = order.get_due();
            var amt = order.display_input_buffer();
            var reedemable_amount = order.display_redeem_points();
            var partner=order.get_client();
            var extradue = 0;
            if (due && lines.length && due !== order.get_due(lines[lines.length - 1])) {
                if (amt == 0){
                    extradue = due;
                }
                else
                    extradue = due - amt;
            }
    
            this.$('.js_redeem_amount').click(function(){
                 self.gui.show_popup('customtextinput',{
                    'title': _t('Redeem Loyalty Points'),
                
                    confirm: function() {

                        // rpc.query({
                        //     model: 'res.partner',
                        //     method: 'get_redeem_points',
                        //     args: [[],[order_list, order, lines, due, amt, reedemable_amount, partner]],
                        //     })
                        //     .then(function(values){
                        //         var pos_amount = values['amount_per_point']
                        //         select_amount = points*pos_amount
                        //     });

                        redeem_point = this.inputbuffer;
                        if(redeem_point> order.display_redeem_points()){
                            self.gui.show_popup('error',{
                                'title': _t('Error'),
                                'body':  _t('Redeem point can not be greater than total points'),
                            });
                            redeem_point=0;
            
                        }
                        order.point_to_use=redeem_point
                        var amount_to_minus=order.calculate_amount(redeem_point)
                        if (amount_to_minus>order.get_due()){
                            this.gui.show_popup('error',{
                                'title': _t('Error'),
                                'body':  _t('Redeem point amount can not be greater than total amount'),
                            });
                            redeem_point=0;
                        }
                        return redeem_point;
                    },
                
                });

                return false;
            });

            this.$('.paymentlines-container').empty();
            var lines = $(QWeb.render('PaymentScreen-Paymentlines', {
                widget: this,
                order: order,
                paymentlines: lines,
                extradue: extradue,
                reedemable_amount: reedemable_amount,
            }));
            lines.on('click', '.delete-button', function() {
                self.click_delete_paymentline($(this).data('cid'));
            });

            lines.on('click', '.paymentline', function() {
                self.click_paymentline($(this).data('cid'));
            });

            lines.appendTo(this.$('.paymentlines-container'));
        },

       


        close: function() {

            this._super();
        }
    });



});

