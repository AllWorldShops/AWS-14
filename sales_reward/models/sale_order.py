# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import date, timedelta
from odoo.http import request


class SalesOrder(models.Model):
    _inherit = "sale.order"
    total_web_points = fields.Integer(string="Your Total website Reward Points")
    point_to_use = fields.Integer()
    amount_into_points=fields.Monetary('amount_into_points', compute="_compute_rem_amt") 
    remaining_points=fields.Integer(compute="_compute_rem_amt")
    customer_type_check=fields.Boolean('Check customer type', compute='check_customer_type', default=True)
    # amount_untaxed_without_point = fields.Monetary(string='Without reedeem point',compute='_amount_all',store=True,readonly=True,default=0)
   
    @api.onchange('partner_id')
    def check_customer_type(self):
        if(self.partner_id.customer_type=='exp'):
            self.customer_type_check=False
        else:
            self.customer_type_check=True


    @api.onchange('partner_id')
    def get_partner_points(self):
        settings=self.env['res.partner'].get_setting_values()
        if settings['is_website_reward'] and self.partner_id.customer_type:
            self.total_web_points = self.partner_id.total_points
        else:
            self.total_web_points = 0

    @api.onchange('point_to_use')
    def calculate_redeemed_points(self):
        settings=self.env['res.partner'].get_setting_values()
        if settings['is_website_reward']and self.partner_id.customer_type:
            if self.partner_id.customer_type == 'ind':
                amount_per_point = settings['ind_amount_per_point']
            elif self.partner_id.customer_type == 'pro':
                amount_per_point = settings['prres.currency()o_amount_per_point']
            elif self.partner_id.customer_type == 'vip':
                amount_per_point = settings['vip_amount_per_point']
            else:
                amount_per_point = 0

            amount = self.point_to_use * amount_per_point

            if self.point_to_use > self.partner_id.total_points:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Entered point should not exceed than total points!'),
                }
                self.point_to_use = 0
                return {'warning': warning}
            elif self.point_to_use < 0:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Amount must be positive!'),
                }
                self.point_to_use = 0
                return {'warning': warning}

            elif amount > self.amount_total:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Amount of points must be less than total amount!'),
                }
                return {'warning': warning}
            else:
                self.amount_into_points=amount

    @api.model
    def create(self, values):
        res = super(SalesOrder, self).create(values)
        settings=self.env['res.partner'].get_setting_values()
        if res.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif res.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif res.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        website_amount_per_point = amount_per_point * res.point_to_use
        if(res.point_to_use):
            reward_product = res.get_partner_type_product()
            res.env['sale.order.line'].sudo().create({
                'product_id': reward_product.id,
                'price_unit':reward_product.list_price ,
                'product_uom_qty': -res.point_to_use,
                'order_id': res.id,
                'name': reward_product.name,
            })
        customer_type = self.env['res.partner'].search([('id','=',values['partner_id'])]).customer_type
        if settings['is_website_reward'] and customer_type:
            data = {
                    'total_web_points': res.partner_id.total_points,
                    'point_to_use': res.point_to_use,
                    'amount_into_points':res.amount_into_points#website_amount_per_point,
                    }
        
            res.write(data)
        return res

    def write(self,values):
        if(values.get('point_to_use')):
            reward_product = self.get_partner_type_product()
            findLine = self.order_line.filtered(lambda order_line:order_line.product_id.id==reward_product.id)
            findLine.update({'product_uom_qty':values.get('point_to_use')})
        res = super(SalesOrder, self).write(values)

    @api.constrains('state')
    def pointChecking(self):
        reward_product = self.get_partner_type_product()
        findLine = self.order_line.filtered(lambda order_line:order_line.product_id.id==reward_product.id)
        if(self.point_to_use==0 and self.website_id and findLine):
            vals={'point_to_use':findLine.product_uom_qty,'amount_into_points':findLine.price_subtotal}
            self.update(vals)
            
    def _prepare_invoice(self):
        res = super(SalesOrder, self)._prepare_invoice()
        res['point_to_use'] = self.point_to_use
        res['total_web_points'] = self.total_web_points
        res['amount_into_points'] =self.amount_into_points
        res['remaining_points'] = self.remaining_points
        return res

    @api.onchange('point_to_use')
    def _compute_rem_amt(self):
        settings=self.env['res.partner'].get_setting_values()
        if self.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif self.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif self.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0
        for obj in self:
            obj.remaining_points =  obj.point_to_use
            if settings['is_website_reward'] and obj.partner_id.customer_type:
                obj.amount_into_points = obj.point_to_use * amount_per_point
            else:
                obj.amount_into_points=0.0

    @api.model
    def is_number(self, s):
        try:
            int(s)
        except ValueError:
            return False

        return True

    @api.model
    def change_selected_redeemable_amount(self, values, user):
        if self.is_number(str(values)):
            website_sale_id = user.last_website_so_id
        settings=self.env['res.partner'].get_setting_values()
        if user.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif user.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif user.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0
       
        valid_point_amount = 0
        for line in self.order_line:
            if line.discount == 0:
                valid_point_amount += line.price_subtotal

        try:
            if settings['is_website_reward'] :
                if settings['is_website_reward'] and not amount_per_point:
                    warning = {
                        'title': ('Warning!'),
                        'message': ('Please select redeem percentage and rewards percentage from Rewards Settings')
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning, 'error':'1'}

                elif int(values) > user.total_points:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Entered point should not exceed than total web points!'),
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning,'error':'2'}
                elif int(values) < 0:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Point must be positive!'),
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning,'error':'3'}
                elif (int(values)*amount_per_point) > website_sale_id.amount_total:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Point amount must be less than Total amount!'),
                    }
                    return {'warning': warning,'error':'4'}
                elif valid_point_amount < int(values)*amount_per_point:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Enter Valid Points. Discounted product can not reedem loyalty points!'),
                    }
                    return {'warning': warning,'error':'5'}
                elif int(values) > 0 and date.today() > user.validity_redeem_points:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Validity of Redeem Points is Expired!'),
                    }
                    return {'warning': warning,'error':'6'}
                elif(int(settings['point_reedem_per_order'])<int(values)):
                    warning = {
                        'title': _('Warning!'),
                        'message': _("You can't reedem point greator than"),
                    }
                    return {'warning':warning,'error':'8'}
                else:
                    reward_product=website_sale_id.get_partner_type_product()
                    findLine = website_sale_id.order_line.filtered(lambda order_line:order_line.product_id.id==reward_product.id)
                    print(findLine)
                    if(website_sale_id and values and findLine):
                        findLine.update({'product_uom_qty':values})
                    elif(website_sale_id and values and (not findLine)):
                        website_sale_id.env['sale.order.line'].sudo().create({
                            'product_id': reward_product.id,
                            'price_unit':-amount_per_point,
                            'product_uom': 1,
                            'product_uom_qty': int(values) or 0,
                            'order_id': website_sale_id.id,
                            'name': reward_product.name,
                        })
                    website_sale_id.point_to_use = int(values)
                    website_sale_id.remaining_points= int(values)
                    website_sale_id.update({
                        'point_to_use':int(values),
                        'amount_into_points': int(values)*amount_per_point,
                    })
                    return True
        except ValueError:
            warning = {
                        'title': _('Warning!'),
                        'message': _('Enter Integer Value!'),
                    }
            return {'warning': warning,'error':'7'}

    def get_partner_type_product(self):
        reward_product=0
        if(self.partner_id.customer_type=='ind'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_ind')])
        elif(self.partner_id.customer_type=='vip'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_vip')])
        elif(self.partner_id.customer_type=='pro'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_pro')])
        return reward_product

class ResetWebsitePoint(models.Model):
    _inherit='website'
    
    def sale_reset(self):
        web_order = request.env['sale.order'].sudo().search([('id','=',request.session['sale_order_id'])])
        web_order.update({'point_to_use':0,'amount_into_points':0})
        res = super(ResetWebsitePoint,self).sale_reset()
        
class EarnPointFunctionalit(models.Model):
    _inherit='stock.picking'

    @api.constrains('state')
    def earn_point(self):
        valid_point_redeem=self.sale_id.amount_total
        settings = self.env['res.partner'].get_setting_values()
        if(self.state=='done' and settings['point_credit_cond']=='complete'):
            if(int(settings['earn_point_mini_amount']) < valid_point_redeem):
                if(settings['amount_value_point']):
                    self.sale_id.partner_id.total_points += (round(valid_point_redeem)/settings['amount_value_point'])*settings['points_for_amount']
                    self.sale_id.partner_id.total_points -= self.sale_id.point_to_use

        