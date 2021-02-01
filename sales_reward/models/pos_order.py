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

_logger = logging.getLogger(__name__)

class CustomPosOrderCreate(models.Model):
    _inherit = "pos.order"
    amount_into_points = fields.Float(string="Reward Points")
    total_pos_points = fields.Integer(string="Total points")
    point_to_use = fields.Integer(string="Select Points to use")
    amount_of_pos_point = fields.Float(string="Amount per POS point")
    customer_type_check=fields.Boolean('Check customer type', compute='check_customer_type', default=True)
    

    @api.onchange('partner_id')
    def check_customer_type(self): 
        if(self.partner_id.customer_type=='exp'):
            self.customer_type_check=False
        else:
            self.customer_type_check=True
        print("!!!!!Sale rewards",self.customer_type_check)

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
       
        if order['data']['point_to_use'] == '':
            order['data']['point_to_use'] = 0
        if (valid_point_amount < (int(float(order['data']['point_to_use'])) * amount_per_point)):
            raise UserError(_("Enter Valid Points. Discounted product can't reedem loyalty point."))

        if (int(order['data']['point_to_use']) > 0 and date.today() > customer.validity_redeem_points):
            raise UserError(_("Validity of Redeem Points is Expired."))

        order1 = super(CustomPosOrderCreate, self)._process_order(order, draft, existing_order)

        pos_order = self.env['pos.order'].search([('id', '=', order1)])

        if customer:
            if pos_order.amount_total >= 0:
                valid_point_redeem = 0
                valid_point_redeem_cat = settings['valid_product_category']

                for line in pos_order.lines:
                    if line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
                        valid_point_redeem += line.price_subtotal

                customer.total_points += round(valid_point_redeem)
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

                customer.total_amount = customer.total_points * amount_per_point
                pos_order.total_pos_points = customer.total_points
                pos_order.amount_of_pos_points = customer.total_amount
                pos_order.amount_into_points = pos_order.point_to_use * amount_per_point

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
                        customer.total_points -= pos_order.point_to_use
                    if customer.customer_type == 'ind':
                        amount_per_point = settings['ind_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)
                    elif customer.customer_type == 'pro':
                        amount_per_point = settings['pro_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)
                    elif customer.customer_type == 'vip':
                        amount_per_point = settings['vip_amount_per_point']
                        customer.total_amount -= (pos_order.point_to_use * amount_per_point)
                        pos_order.remaining_points = customer.total_points - pos_order.point_to_use
            customer.backup = pos_order.point_to_use
            pos_order.amount_into_points = pos_order.point_to_use * amount_per_point

            
            if pos_order.point_to_use:
               

                customer.total_points -= pos_order.point_to_use
                customer.total_amount -= (pos_order.point_to_use*amount_per_point)
                self.partner_id.remaining_points = customer.total_points-pos_order.point_to_use    
          
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