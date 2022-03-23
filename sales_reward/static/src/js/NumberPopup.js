odoo.define('sales_reward.NumberPopup', function(require) {
    'use strict';

    const { useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ObjPosComponent = require('point_of_sale.PosComponent');
    var rpc = require('web.rpc')
    var models = require('point_of_sale.models');
    var today = new Date()
    var date = today.getFullYear() + '-' + (today.getMonth()+1) + '-' + today.getDate();

    models.load_fields('res.partner','total_points');
    models.load_fields('res.partner','customer_type');
    models.load_fields('res.partner','validity_redeem_points');
    models.load_fields('pos.order','point_to_use','pos_point_to_use','total_pos_points','amount_into_points','amount_of_pos_point','customer_type_check','set_customer_type');

    // formerly NumberPopupWidget
    class NumberPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {Boolean} props.isPassword Show password popup.
         * @param {number|null} props.startingValue Starting value of the popup.
         *
         * Resolve to { confirmed, payload } when used with showPopup method.
         * @confirmed {Boolean}
         * @payload {String}
         */
        constructor() {
            super(...arguments);
            useListener('accept-input', this.confirm);
            useListener('close-this-popup', this.cancel);
            let startingBuffer = '';
            if (typeof this.props.startingValue === 'number' && this.props.startingValue > 0) {
                startingBuffer = this.props.startingValue.toString();
            }
            this.state = useState({ buffer: startingBuffer });
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                triggerAtEnter: 'accept-input',
                triggerAtEscape: 'close-this-popup',
                state: this.state,
            });
        }
        get decimalSeparator() {
            return this.env._t.database.parameters.decimal_point;
        }
        get inputBuffer() {
            if (this.state.buffer === null) {
                return '';
            }
            if (this.props.isPassword) {
                return this.state.buffer.replace(/./g, '•');
            } else {
                return this.state.buffer;
            }
        }
        sendInput(key) {
            this.trigger('numpad-click-input', { key });
        }
        getPayload() {
            return NumberBuffer.get();
        }
        click_confirm(){
            this.trigger('close-popup');
            var type_customer = ''
            var redeem_point = this.inputBuffer;
            var order = this.env.pos.get_order();
            var customer = this.env.pos.get_client();
            this.env.pos.rpc({
                model: 'res.partner',
                method: 'get_reward_amount',
                args: [[],[order]],
           }).then(function(values){
                sessionStorage.setItem('ind',values['ind']);
                sessionStorage.setItem('pro',values['pro']);
                sessionStorage.setItem('vip',values['vip']);
                sessionStorage.setItem('exp',values['exp']);
            });

           this.env.pos.rpc({
                model: 'pos.order',
                method: 'get_customer_type',
                args: [[],[customer.id]],
           }).then(function(values){
                if(values){
                    var type_customer = values
                }
           });

            if(redeem_point > order.display_redeem_points()){
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Redeem point can not be greater than total points!'),
                });
                redeem_point=0;
            }
            order.point_to_use = redeem_point
            customer.point_to_use = redeem_point
            customer.pos_point_to_use = redeem_point
            var amount_to_minus = order.calculate_amount(redeem_point)

            if (customer){
                var customer_type = customer.customer_type
            }
            var amount_per_point = redeem_point * parseInt(sessionStorage.getItem(customer_type))
//            if (amount_per_point > order.get_due()){
//            if (amount_per_point > order.get_total_with_tax()){
            if (amount_per_point > order.custom_get_total_with_tax()){
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Redeem Amount can not be greater than total amount!'),
                });

                redeem_point=0;

            }
            if (today.getDate() > customer.validity_redeem_points){
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Validity of Redeem Points is Expired!'),
                });
                redeem_point=0;
            }

            order.point_to_use = redeem_point
            customer.point_to_use = redeem_point
            customer.pos_point_to_use = redeem_point

            return redeem_point;
        }
    }
    NumberPopup.template = 'NumberPopup';
    NumberPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Confirm ?',
        body: '',
        cheap: false,
        startingValue: null,
        isPassword: false,
    };

    Registries.Component.add(NumberPopup);

    return NumberPopup;
});
