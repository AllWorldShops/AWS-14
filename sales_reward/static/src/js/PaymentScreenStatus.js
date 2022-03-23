odoo.define('sales_reward.PaymentScreenStatus', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PaymentScreenStatus extends PosComponent {
        get changeText() {
            return this.env.pos.format_currency(this.currentOrder.get_change());
        }
        get totalDueText() {
            return this.env.pos.format_currency(
                this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
            );
        }
        get remainingText() {
            return this.env.pos.format_currency(
                this.currentOrder.get_due() > 0 ? this.currentOrder.get_due() : 0
            );
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        get display_redeem_points() {
//            return (this.env.pos.get_order().redeem_points());
            return (this.currentOrder.redeem_points());
//            return (this.currentOrder.get_new_total_points());
        }
        get selected_redeem_points() {
            if(this.env.pos.get_order()){
                if(this.env.pos.get_order().display_input_buffer()){

                    return (this.env.pos.get_order().display_input_buffer());
                }
                else{
                    return 0;
                }
            }
            else{
                return 0;
            }
//            this.env.pos.get_order().display_input_buffer().reload()
        }

        get redeem_amount() {
            if (this.env.pos.get_order().set_redeem_point()){

            return this.env.pos.format_currency((this.env.pos.get_order().set_redeem_point()));

            }
            else{
                return this.env.pos.format_currency(0);
            }
        }
    }
    PaymentScreenStatus.template = 'PaymentScreenStatus';

    Registries.Component.add(PaymentScreenStatus);

    return PaymentScreenStatus;
});
