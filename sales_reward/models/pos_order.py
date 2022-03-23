# -*- coding: utf-8 -*-

import logging
from datetime import date, timedelta
from functools import partial
import psycopg2
import pytz
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, Warning
from odoo.http import request
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class CustomPosOrderCreate(models.Model):
    _inherit = "pos.order"

    amount_into_points = fields.Float(string="Reward Points")
    total_pos_points = fields.Float(string="Total points")
    point_to_use = fields.Float(string="Select Points to use")
    pos_point_to_use = fields.Float(string="Select Pos Points to use")
    amount_of_pos_points = fields.Float(string="Amount per POS point")
    customer_type_check=fields.Boolean('Check customer type', compute='check_customer_type', default=True)
    # remaining_points = fields.Integer(string="Remaining Points")
    set_customer_type = fields.Char("Customer type", compute='get_customer_type')

    @api.onchange('partner_id')
    def get_customer_type(self, id):

        partner_id = self.env['res.partner'].search([('id','=',id[0])])
        if partner_id.customer_type == 'ind':
            customer_type = 'ind'
        elif partner_id.customer_type == 'pro':
            customer_type = 'pro'
        elif partner_id.customer_type == 'vip':
            customer_type = 'vip'
        else:
            customer_type = 'exp'

        return customer_type

    @api.onchange('partner_id')
    def check_customer_type(self):
        if(self.partner_id.customer_type=='exp'):
            self.customer_type_check=False
        else:
            self.customer_type_check=True


    def get_partner_type_product(self):
        reward_product = 0
        if (self.partner_id.customer_type == 'ind'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_ind')])
        elif (self.partner_id.customer_type == 'vip'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_vip')])
        elif (self.partner_id.customer_type == 'pro'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_pro')])
        return reward_product

    @api.model
    def _process_order(self, order, draft, existing_order):
        settings = self.env['res.partner'].get_setting_values()

        valid_point_amount = 0
        for line in order['data']['lines']:

            if line[2]['discount'] == 0:
                valid_point_amount += line[2]['price_subtotal']

        customer = self.env['res.partner'].search([('id', '=', order['data']['partner_id'])])
        if customer.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif customer.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif customer.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        if 'point_to_use' not in order['data']:
            order['data'].update({'point_to_use':0})
        if order['data']['point_to_use'] == '':
            order['data']['point_to_use'] = 0

        # if (valid_point_amount < (int(float(order['data']['point_to_use'])) * amount_per_point)):
        #     raise UserError(_("Enter Valid Points. Discounted product can't redeem loyalty point."))

        # if (int(order['data']['point_to_use']) > 0 and date.today() > customer.validity_redeem_points):
        #     raise UserError(_("Validity of Redeem Points is Expired."))

        order1 = super(CustomPosOrderCreate, self)._process_order(order, draft, existing_order)

        pos_order = self.env['pos.order'].search([('id', '=', order1)])

        if customer:
            if pos_order.amount_total >= 0:
                valid_point_redeem = pos_order.amount_total
                valid_point_redeem_cat = settings['valid_product_category']

#                 if valid_point_redeem_cat:
#                     for line in pos_order.lines:
#                         if line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
#                             valid_point_redeem += line.price_subtotal

                # customer.total_points += round(valid_point_redeem)
                if customer.customer_type == 'ind':
                    amount_per_point = settings['ind_amount_per_point']
                    point_duration = settings['ind_point_duration']
                elif customer.customer_type == 'pro':
                    amount_per_point = settings['pro_amount_per_point']
                    point_duration = settings['pro_point_duration']
                elif customer.customer_type == 'vip':
                    amount_per_point = settings['vip_amount_per_point']
                    point_duration = settings['vip_point_duration']
                else:
                    amount_per_point = 0
                    point_duration = 0

                if not amount_per_point:
                    amount_per_point = 0

                # customer.total_amount = customer.total_points * amount_per_point
                # pos_order.total_pos_points = customer.total_points
                # pos_order.amount_of_pos_points = customer.total_amount
                # pos_order.amount_into_points = pos_order.point_to_use * amount_per_point

                if (round(valid_point_redeem) > 0):
                    pos_order.partner_id.validity_redeem_points = date.today() + timedelta(days=point_duration)

            else:
                customer.total_points += 0


            if 'point_to_use' in order['data'].keys():
                if order['data']['point_to_use']:
                    try:
                        pos_order.point_to_use = order['data']['point_to_use']
                    except ValueError:
                        pos_order.point_to_use = order['data']['point_to_use'].split('.')[0]

                    # customer.total_points -= pos_order.point_to_use

                    if customer.customer_type == 'ind':
                        amount_per_point = settings['ind_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)
                    elif customer.customer_type == 'pro':
                        amount_per_point = settings['pro_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)
                    elif customer.customer_type == 'vip':
                        amount_per_point = settings['vip_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)

            if pos_order['point_to_use'] != 0:
                reward_product = pos_order.get_partner_type_product()
                pos_order.env['pos.order.line'].create({
                    'product_id': reward_product.id,
                    'price_unit': -amount_per_point,
                    # 'product_uom': 1,
                    'qty': pos_order['point_to_use'] or 0,
                    'order_id': pos_order.id,
                    'price_subtotal': -amount_per_point * int(float(pos_order['point_to_use'])),
                    'price_subtotal_incl': -amount_per_point * int(float(pos_order['point_to_use'])),
                    'full_product_name': reward_product.name,
                })

            # remaining_points = customer.total_points - pos_order.point_to_use
            # customer.backup = pos_order.point_to_use
            # pos_order.amount_into_points = pos_order.point_to_use * amount_per_point

            valid_point_redeem = pos_order.amount_total
            valid_point_redeem_cat = settings['valid_product_category']

#             if valid_point_redeem_cat:
#                 for line in pos_order.lines:
#                     if line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
#                         valid_point_redeem += line.price_subtotal

            # reward_product = self.get_partner_type_product()
            reward_product = pos_order.get_partner_type_product()
#             reward_product_sum = 0
#             for line in pos_order.lines:
#                 if line.product_id == reward_product:
#                     reward_product_sum += line.price_subtotal

            if amount_per_point != 0:
                earn_points = ((valid_point_redeem) / amount_per_point)
            else:
                earn_points = 0

            customer.total_points += round(earn_points)


            customer.total_amount = customer.total_points * amount_per_point
            pos_order.total_pos_points = customer.total_points
            pos_order.amount_of_pos_points = customer.total_amount
            pos_order.amount_into_points = pos_order.point_to_use * amount_per_point


            if pos_order.point_to_use:
                customer.total_points -= pos_order.point_to_use
                customer.total_amount -= (pos_order.point_to_use*amount_per_point)
                self.partner_id.remaining_points = customer.total_points-pos_order.point_to_use
                
                
                print("point_to use")
                point_to_use = pos_order.point_to_use
                expire_ids = self.env['reward.expire'].search([('partner_id','=',customer.id),('remaining_reward_point','>',0)], order = "reward_date asc")
                used_point = 0
                for expire_id in expire_ids:
                    print(expire_id.reward_date)
                    remaining_reward_point = expire_id.remaining_reward_point
                    used_point = point_to_use
                    point_to_use = point_to_use - expire_id.remaining_reward_point
                    if point_to_use < 0:
                        expire_id.remaining_reward_point = abs(point_to_use)
                        expire_id.used_reward_point = expire_id.used_reward_point+abs(used_point)
                        break
                    elif point_to_use > 0:
                        expire_id.remaining_reward_point = 0
                        expire_id.used_reward_point = expire_id.used_reward_point+remaining_reward_point
                    elif point_to_use == 0:
                        expire_id.remaining_reward_point = 0
                        expire_id.used_reward_point = expire_id.used_reward_point+remaining_reward_point
                        break
            
            if earn_points > 0:
                expire_vals={
                        'reward_option':'pos',
                        'reward_date':fields.Datetime.now(),
                        'reward_expire_date':fields.Datetime.now() + relativedelta(years=1),
                        'reward_point':round(earn_points),
                        'remaining_reward_point':round(earn_points),
                        'amount_per_point':amount_per_point,
                        'partner_id':pos_order.partner_id.id,
                        'pos_id':pos_order.id,
                        }
                expire_id = self.env['reward.expire'].create(expire_vals)
                print(expire_id)
                
                

            if settings['is_send_mail'] and pos_order.partner_id:

                template = self.env.ref('sales_reward.custom_email_view')
                self.env['mail.template'].browse(template.id).send_mail(pos_order.partner_id.id)


            res = self.env['account.move'].search([('invoice_origin', '=', pos_order.name )])
            if res:
                data ={
                   'point_to_use': pos_order.point_to_use,
                   'amount_into_points': pos_order.amount_into_points,
                   'amount_total': pos_order.amount_total,
                   'amount_residual': 0.0

                  }
                res.write(data)
        return order1


    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        settings=self.env['res.partner'].get_setting_values()
        for order in self:
            order.amount_paid = order.amount_return = order.amount_tax = 0.0
            currency = order.pricelist_id.currency_id
            order.amount_paid = sum(payment.amount for payment in order.statement_ids)
            order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
            order.amount_tax = currency.round(
                sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            if order.partner_id.customer_type == 'ind':
                amount_per_point = settings['ind_amount_per_point']
                amount_to_minus = order.point_to_use*amount_per_point
            elif order.partner_id.customer_type == 'pro':
                amount_per_point = settings['pro_amount_per_point']
                amount_to_minus = order.point_to_use*amount_per_point
            elif order.partner_id.customer_type == 'vip':
                amount_per_point = settings['vip_amount_per_point']
                amount_to_minus = order.point_to_use*amount_per_point
            else:
                amount_to_minus = 0
            order.amount_total = order.amount_tax + amount_untaxed - amount_to_minus

            amount_total = order.amount_total



    def test_paid(self):
        for order in self:
            order.amount_total= order.amount_paid-order.amount_into_points

            if order.lines and not order.amount_total:
                continue
            if (not order.lines) or (not order.statement_ids) or (abs(order.amount_total - order.amount_paid) > 0.00001):
                return False
        return True