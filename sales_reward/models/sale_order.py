# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta
from odoo.http import request
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class SalesOrder(models.Model):
    _inherit = "sale.order"

    total_web_points = fields.Integer(string="Your Total website Reward Points")
    point_to_use = fields.Integer(readonly = True)
    amount_into_points = fields.Monetary('amount_into_points', compute="_compute_rem_amt")
    remaining_points = fields.Integer(compute="_compute_rem_amt")
    customer_type_check = fields.Boolean('Check customer type', compute='check_customer_type', default=True)
    # amount_untaxed_without_point = fields.Monetary(string='Without reedeem point',compute='_amount_all',store=True,readonly=True,default=0)
    is_website = fields.Boolean('is_website', compute='check_website', default=True)
    earn_points_per_order = fields.Integer(string="Earned Points")

    @api.onchange('partner_id')
    def check_customer_type(self):
        if (self.partner_id.customer_type == 'exp'):
            self.customer_type_check = False
        else:
            self.customer_type_check = True

    @api.onchange('partner_id')
    def get_partner_points(self):
        settings = self.env['res.partner'].get_setting_values()
        if settings['is_website_reward'] and self.partner_id.customer_type:
            self.total_web_points = self.partner_id.total_points
        else:
            self.total_web_points = 0

    @api.onchange('point_to_use')
    def calculate_redeemed_points(self):

        settings = self.env['res.partner'].get_setting_values()
        amount_per_point = 0
        if settings['is_website_reward'] and self.partner_id.customer_type:
            if self.partner_id.customer_type == 'ind':
                amount_per_point = settings['ind_amount_per_point']
            elif self.partner_id.customer_type == 'pro':
                amount_per_point = settings['res.currency()o_amount_per_point']
            elif self.partner_id.customer_type == 'vip':
                amount_per_point = settings['vip_amount_per_point']
            else:
                amount_per_point = 0

            if not amount_per_point:
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
                self.amount_into_points = amount

    @api.model
    def create(self, values):
        res = super(SalesOrder, self).create(values)
        settings = self.env['res.partner'].get_setting_values()
        if res.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
            if not amount_per_point:
                amount_per_point = 0
        elif res.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif res.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        if res.point_to_use:
            website_amount_per_point = amount_per_point * res.point_to_use

        if (res.point_to_use):
            reward_product = res.get_partner_type_product()
            res.env['sale.order.line'].sudo().create({
                'product_id': reward_product.id,
                'price_unit': reward_product.list_price,
                'product_uom_qty': -res.point_to_use,
                'order_id': res.id,
                'name': reward_product.name,
            })
        customer_type = self.env['res.partner'].search([('id', '=', values['partner_id'])]).customer_type
        if settings['is_website_reward'] and customer_type:
            data = {
                'total_web_points': res.partner_id.total_points,
                'point_to_use': res.point_to_use,
                'amount_into_points': res.amount_into_points  # website_amount_per_point,
            }

            res.write(data)
        return res

    def write(self, values):
        if (values.get('point_to_use')):
            reward_product = self.get_partner_type_product()
            findLine = self.order_line.filtered(lambda order_line: order_line.product_id.id == reward_product.id)
            findLine.update({'product_uom_qty': values.get('point_to_use')})
        res = super(SalesOrder, self).write(values)

    @api.constrains('state')
    def pointChecking(self):
        reward_product = self.get_partner_type_product()
        findLine = self.order_line.filtered(lambda order_line: order_line.product_id.id == reward_product.id)
        if (self.point_to_use == 0 and self.website_id and findLine):
            vals = {'point_to_use': findLine.product_uom_qty, 'amount_into_points': findLine.price_subtotal}
            self.update(vals)

    def _prepare_invoice(self):
        res = super(SalesOrder, self)._prepare_invoice()
        res['point_to_use'] = self.point_to_use
        res['total_web_points'] = self.total_web_points
        res['amount_into_points'] = self.amount_into_points
        res['remaining_points'] = self.remaining_points
        return res

    @api.depends('order_line.price_total', 'partner_id')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """

        settings = self.env['res.partner'].get_setting_values()
        if self.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif self.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif self.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        if self.point_to_use:
            amount_to_minus = self.point_to_use * amount_per_point
        else:
            amount_to_minus = 0

        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax

            if ((amount_untaxed) + amount_tax) <= 0:
                order.update({
                    'amount_untaxed': 0,
                    'amount_tax': 0,
                    'amount_total': 0,
                })
                warning = {
                    'title': ('Warning!'),
                    'message': ("Invalid")
                }

                return {'warning': warning, 'error': '11'}
            else:
                order.update({
                    'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_total': (amount_untaxed) + amount_tax,
                })

    @api.onchange('point_to_use')
    def _compute_rem_amt(self):

        settings = self.env['res.partner'].get_setting_values()
        if self.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif self.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif self.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        # for obj in self:
        #     obj.remaining_points = obj.point_to_use
        #     if settings['is_website_reward'] and obj.partner_id.customer_type:
        #         obj.amount_into_points = obj.point_to_use * amount_per_point
        #     else:
        #         obj.amount_into_points=0.0

        list_prod_id = []
        for obj in self:
            reward_product = obj.get_partner_type_product()

            if len(obj.order_line.ids) > 0:
                for line in obj.order_line:
                    list_prod_id.append(line.product_id)
            else:
                list_prod_id = []

            if reward_product:
                if reward_product in list_prod_id:
                    obj.remaining_points = obj.point_to_use
                    if settings['is_website_reward'] and obj.partner_id.customer_type:
                        obj.amount_into_points = obj.point_to_use * amount_per_point
                    else:
                        obj.amount_into_points = 0.0
                else:
                    obj.remaining_points = 0
                    obj.point_to_use = 0
                    obj.amount_into_points = 0.0
            else:
                obj.remaining_points = 0
                obj.point_to_use = 0
                obj.amount_into_points = 0.0

    @api.model
    def is_number(self, s):
        try:
            int(s)
        except ValueError:
            return False

        return True

    @api.model
    @api.onchange('partner_id')
    def check_website(self):
        if self.website_id:
            self.is_website = True
        else:
            self.is_website = False

    @api.model
    def change_selected_redeemable_amount(self, values, user):
#         if self.is_number(str(values)):
        website_sale_id = user.last_website_so_id
        settings = self.env['res.partner'].get_setting_values()
        if user.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif user.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif user.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        valid_point_amount = 0
        for line in self.order_line:
            if line.discount == 0:
                valid_point_amount += line.price_subtotal

        custom_amount_total = 0
        reward_product = website_sale_id.get_partner_type_product()
        for line in website_sale_id.order_line:
            if line.discount == 0:
                if line.product_id.id != reward_product.id:
                    custom_amount_total += line.price_subtotal

        try:
            if settings['is_website_reward']:
                if settings['is_website_reward'] and not amount_per_point:
                    warning = {
                        'title': ('Warning!'),
                        'message': ('Please select redeem percentage and rewards percentage from Rewards Settings')
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning, 'error': '1'}

                elif int(values) > user.total_points:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Entered point should not exceed than total web points!'),
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning, 'error': '2'}
                elif int(values) < 0:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Point must be positive!'),
                    }
                    website_sale_id.total_web_points = 0.0
                    website_sale_id.point_to_use = 0.0
                    return {'warning': warning, 'error': '3'}
                # elif (int(values)*amount_per_point) > website_sale_id.amount_total:
                elif (int(values) * amount_per_point) > custom_amount_total:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Point amount must be less than Total amount!'),
                    }
                    return {'warning': warning, 'error': '4'}
                elif valid_point_amount < int(values) * amount_per_point:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Enter Valid Points. Discounted product can not redeem loyalty points!'),
                    }
                    return {'warning': warning, 'error': '5'}
#                 elif int(values) > 0 and date.today() > user.validity_redeem_points:
#                     warning = {
#                         'title': _('Warning!'),
#                         'message': _('Validity of Redeem Points is Expired!'),
#                     }
#                     return {'warning': warning, 'error': '6'}
                elif (int(settings['point_reedem_per_order']) < int(values)):
                    warning = {
                        'title': _('Warning!'),
                        'message': _("You can't redeem point greater than"),
                    }
                    return {'warning': warning, 'error': '8'}
                else:
                    reward_product = website_sale_id.get_partner_type_product()
                    findLine = website_sale_id.order_line.filtered(
                        lambda order_line: order_line.product_id.id == reward_product.id)
                    print(findLine)
                    if (website_sale_id and values and findLine):
                        findLine.update({'product_uom_qty': values})
                    elif (website_sale_id and values and (not findLine)):
                        website_sale_id.env['sale.order.line'].sudo().create({
                            'product_id': reward_product.id,
                            'price_unit': -amount_per_point,
                            'product_uom': 1,
                            'product_uom_qty': int(values) or 0,
                            'order_id': website_sale_id.id,
                            'name': reward_product.name,
                            'qty_delivered': int(values),
                            'qty_invoiced': int(values),
                        })
                    website_sale_id.point_to_use = int(values)
                    website_sale_id.remaining_points = int(values)

                    product_list = []
                    for line in website_sale_id.order_line:
                        product_list.append(line.product_id)

                    reward_product.list_price = -amount_per_point

                    if reward_product in product_list:
                        website_sale_id.point_to_use = int(values)
                        website_sale_id.remaining_points = int(values)
                    else:
                        website_sale_id.point_to_use = 0
                        website_sale_id.remaining_points = 0

                    # website_sale_id.update({
                    #     'point_to_use':int(values),
                    #     'amount_into_points': int(values)*amount_per_point,
                    # })
                    website_sale_id.update({
                        'amount_into_points': int(values) * amount_per_point,
                        'amount_untaxed': website_sale_id.pricelist_id.currency_id.round(
                            website_sale_id.amount_untaxed),
                        'amount_tax': website_sale_id.pricelist_id.currency_id.round(website_sale_id.amount_tax),
                        'amount_total': website_sale_id.amount_untaxed + website_sale_id.amount_tax,
                    })

                    return True

        except ValueError:
            warning = {
                'title': _('Warning!'),
                'message': _('Enter Integer Value!'),
            }
            return {'warning': warning, 'error': '7'}

    def get_partner_type_product(self):
        reward_product = 0
        if (self.partner_id.customer_type == 'ind'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_ind')])
        elif (self.partner_id.customer_type == 'vip'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_vip')])
        elif (self.partner_id.customer_type == 'pro'):
            reward_product = self.env['product.product'].search([('default_code', '=', 'reward_pro')])
        return reward_product

    # @api.onchange('point_to_use')
    def so_redeem(self):

        user = self.partner_id
        values = self.point_to_use

        # if self.is_number(str(values)):
        #     website_sale_id = user.last_website_so_id

        settings = self.env['res.partner'].get_setting_values()
        if user.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif user.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif user.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0

        if not amount_per_point:
            amount_per_point = 0

        valid_point_amount = 0
        for line in self.order_line:
            if line.discount == 0:
                valid_point_amount += line.price_subtotal

        custom_amount_total = 0
        reward_product = self.get_partner_type_product()
        for line in self.order_line:
            if line.discount == 0:
                if line.product_id.id != reward_product.id:
                    custom_amount_total += line.price_subtotal

        try:
            if settings['is_website_reward']:
                if settings['is_website_reward'] and not amount_per_point:
                    raise UserError(_('Please select redeem percentage and rewards percentage from Rewards Settings'))
                    self.total_web_points = 0.0
                    self.point_to_use = 0.0

                elif int(values) <= 0:
                    raise UserError(_('Please enter valid amount!'))
                    self.total_web_points = 0.0
                    self.point_to_use = 0.0

                elif int(values) > user.total_points:
                    raise UserError(_('Entered point should not exceed than total web points!'))
                    self.total_web_points = 0.0
                    self.point_to_use = 0.0

                elif int(values) < 0:
                    raise UserError(_('Point must be positive!'))
                    self.total_web_points = 0.0
                    self.point_to_use = 0.0

                # elif (int(values)*amount_per_point) > website_sale_id.amount_total:
                elif (int(values) * amount_per_point) > custom_amount_total:
                    raise UserError(_('Point amount must be less than Total amount!'))

                elif valid_point_amount < int(values) * amount_per_point:
                    raise UserError(_('Enter Valid Points. Discounted product can not redeem loyalty points!'))

#                 elif int(values) > 0 and date.today() > user.validity_redeem_points:
#                     raise UserError(_('Validity of Redeem Points is Expired!'))

                elif (int(settings['point_reedem_per_order']) < int(values)):
                    raise UserError(_("You can't redeem point greater than set limit in settings."))

                else:
                    reward_product = self.get_partner_type_product()
                    findLine = self.order_line.filtered(
                        lambda order_line: order_line.product_id.id == reward_product.id)
                    print(findLine)
                    if (self and values and findLine):
                        findLine.update({'product_uom_qty': values})
                    elif (self and values and (not findLine)):
                        self.env['sale.order.line'].sudo().create({
                            'product_id': reward_product.id,
                            'price_unit': -amount_per_point,
                            'product_uom': 1,
                            'product_uom_qty': int(values) or 0,
                            'order_id': self.id,
                            'name': reward_product.name,
                            'qty_delivered': int(values),
                            'qty_invoiced': int(values),
                        })
                    self.point_to_use = int(values)
                    self.remaining_points = int(values)

                    product_list = []
                    for line in self.order_line:
                        product_list.append(line.product_id)

                    if reward_product != 0:
                        reward_product.list_price = -amount_per_point

                        if reward_product in product_list:
                            self.point_to_use = int(values)
                            self.remaining_points = int(values)
                        else:
                            self.point_to_use = 0
                            self.remaining_points = 0

                    # website_sale_id.update({
                    #     'point_to_use':int(values),
                    #     'amount_into_points': int(values)*amount_per_point,
                    # })
                    self.update({
                        'amount_into_points': int(values) * amount_per_point,
                        'amount_untaxed': self.pricelist_id.currency_id.round(
                            self.amount_untaxed),
                        'amount_tax': self.pricelist_id.currency_id.round(self.amount_tax),
                        'amount_total': self.amount_untaxed + self.amount_tax,
                    })

                    return True

        except ValueError:
            raise UserError(_('Invalid!'))



class ResetWebsitePoint(models.Model):
    _inherit = 'website'

    def sale_reset(self):
        web_order = request.env['sale.order'].sudo().search([('id', '=', request.session['sale_order_id'])])
        # web_order.update({'point_to_use':0,'amount_into_points':0})
        res = super(ResetWebsitePoint, self).sale_reset()


class EarnPointFunctionalit(models.Model):
    _inherit = 'stock.picking'



    @api.constrains('state')
    def earn_point(self):
       # import pdb; pdb.set_trace()
        for each in self:

            valid_point_redeem = each.sale_id.amount_total
            settings = each.env['res.partner'].get_setting_values()
            amount_per_point = 0
            if each.sale_id.partner_id.customer_type == 'ind':
                amount_per_point = settings['ind_amount_per_point']
                if not amount_per_point:
                    amount_per_point = 0
            elif each.sale_id.partner_id.customer_type == 'pro':
                amount_per_point = settings['pro_amount_per_point']
            elif each.sale_id.partner_id.customer_type == 'vip':
                amount_per_point = settings['vip_amount_per_point']
            else:
                amount_per_point = 0

            if not amount_per_point:
                amount_per_point = 0

            earn_points = 0
            if amount_per_point != 0 and valid_point_redeem:
                earn_points = valid_point_redeem / (amount_per_point)
              #  SalesOrder.earn_points_per_order = valid_point_redeem / int(amount_per_point)
               # self.earn_points_per_order = valid_point_redeem / int(amount_per_point)
            else:
                earn_points = 0
                #SalesOrder.earn_points_per_order = 0
                # self.earn_points_per_order = 0

            SalesOrder.earn_points_per_order = earn_points
            if each.state == 'done' and settings['point_credit_cond'] == 'complete' and each.picking_type_code == 'outgoing':
                if (int(settings['earn_point_mini_amount']) < valid_point_redeem):
                    # if (settings['amount_value_point']):
                    #     each.sale_id.partner_id.total_points += (round(valid_point_redeem) / settings[
                    #         'amount_value_point']) * settings['points_for_amount']
                    #     each.sale_id.partner_id.total_points -= each.sale_id.point_to_use
                    each.sale_id.partner_id.total_points += earn_points
                    each.sale_id.partner_id.total_points -= each.sale_id.point_to_use
                    
#                     Added by jana
                    expire_vals={
                                'reward_option':'website',
                                'reward_date':fields.Datetime.now(),
                                'reward_expire_date':fields.Datetime.now() + relativedelta(years=1),
                                'reward_point':int(earn_points),
                                'remaining_reward_point':int(earn_points),
                                'amount_per_point':amount_per_point,
                                'sale_id': each.sale_id.id,
#                                 'invoice_id':invoice_id.id,
                                'partner_id':each.sale_id.partner_id.id,
                                }
                    expire_id = self.env['reward.expire'].create(expire_vals)
                    print(expire_id)
                    
                    print("point_to use")
                    point_to_use = each.sale_id.point_to_use
                    expire_ids = self.env['reward.expire'].search([('partner_id','=',each.sale_id.partner_id.id),('remaining_reward_point','>',0)], order = "reward_date asc")
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
                    
                    
                    
                    
                    
