# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time
import datetime
from datetime import date, timedelta

class SalesRewards(models.Model):
    """Add two new columns to the res.partner model 'Rewards Points' and 'Redeemable Amount'"""
    # _name = 'res.partner'
    _inherit = 'res.partner'

    @api.onchange('customer_type')
    def change(self):
        if self.customer_type == 'exp':
            self.total_points=0

    def sale_reward_number(self):

        for obj in self:
            if(not(obj.customer_type=='exp')):
                sale_card_number=str(obj.id)
                obj.barcode=sale_card_number.zfill(5)
                obj.update({'barcode':obj.barcode})
                obj.sale_reward_card=sale_card_number.zfill(5)

        
    total_web_points = fields.Integer(string="Total website Reward Points")
    total_pos_points=fields.Integer(string="Total POS Reward Points")
    amount_of_web_points = fields.Monetary(string="Amount per website point", readonly=True)
    backup=fields.Float("Backup points for calculations")
    remaining_points=fields.Integer("Remaining Points")
    is_pos_user=fields.Boolean("Is POS user", default=True)
    is_website_user=fields.Boolean("Is website user", default=True)
    amount_of_pos_points=fields.Monetary(string="Amount per POS point", readonly=True)
    birthdate=fields.Date("Birth Date")
    customer_type = fields.Selection([
        ('ind', 'Individual'),
        ('pro', 'Professional'),
        ('vip', 'VIP'),('exp','Export')], default='ind')
    total_points = fields.Integer(string="Total Reward Points", default=0)
    total_amount = fields.Monetary(default=0,string="Total Reward Amount", compute="_compute_total_amount", readonly=True)
    validity_redeem_points = fields.Date(string="Validity of Redeem Points", default=fields.Date.context_today)

    sale_reward_card=fields.Char(string='Loyalty Card Number',compute='sale_reward_number')
    barcode=fields.Char('Barcode',compute='sale_reward_number')
    reward_expire_ids = fields.One2many("reward.expire", "partner_id", string="Sale Reward")


    @api.onchange('total_points','partner_id')
    def _compute_total_amount(self):

        amount_per_point=0
        settings = self.get_setting_values()
        if self.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif self.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif self.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else :
            self.total_amount = 0

        if not amount_per_point:
            self.total_amount = 0
        if amount_per_point is not None:
            self.total_amount = self.total_points*amount_per_point

    def get_redeem_price(self,data):
        customer_type = self.search([('id','=',data[0]['client']['id'])]).customer_type
        settings = self.get_setting_values()
        if customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
        elif customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
        elif customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
        else:
            amount_per_point = 0
        values = {'amount_per_point': amount_per_point}
        return values


    def get_reward_amount(self, data):
        settings = self.get_setting_values()
        values = {'ind': settings['ind_amount_per_point'], 'pro': settings['pro_amount_per_point'],
                  'vip': settings['vip_amount_per_point'], 'exp': 0}
        return values

    def email_trigger_action(self):
        settings=self.env['res.partner'].get_setting_values()

        today = datetime.datetime.today().strftime('%m-%d')

        customer_data = self.env['res.partner'].search([('id', '>', "0")])
        for val in customer_data:
            if val.birthdate:

                birth_date = val.birthdate.strftime('%m-%d')
                if birth_date == today:
                    if settings['is_birthday_points'] :
                        birthdate_points=settings['birthday_points']
                        if settings['is_website_reward'] and val.is_website_user:
                            val.total_points += birthdate_points
                            val.total_web_points+=birthdate_points
                            val.amount_of_web_points= val.total_web_points*(settings['website_amount_per_point'])
                        elif settings['is_pos_reward'] and val.is_pos_user:
                            val.total_points += birthdate_points
                            val.total_pos_points+=birthdate_points
                            val.amount_of_pos_points=val.total_pos_points*(settings['pos_amount_per_point'])
                        self.create_send_mail(val)
        return True

#     def check_point_validity(self):
#         """Cron for Checking validity of points"""
#         customers = self.search([('validity_redeem_points', '<', date.today())])
#         for customer in customers:
#             if not customer.total_points == 0:
#                 customer.total_points = 0

    def get_setting_values(self):

        values={}
        ir_values = self.env['ir.default']
        vip_amount_per_point = ir_values.get('res.config.settings', 'vip_amount_per_point')
        pro_amount_per_point = ir_values.get('res.config.settings', 'pro_amount_per_point')
        ind_amount_per_point = ir_values.get('res.config.settings', 'ind_amount_per_point')

        valid_product_category = ir_values.get('res.config.settings', 'valid_product_category')

        vip_point_duration = ir_values.get('res.config.settings', 'vip_point_duration')
        pro_point_duration = ir_values.get('res.config.settings', 'pro_point_duration')
        ind_point_duration = ir_values.get('res.config.settings', 'ind_point_duration')
        
        is_website_reward = ir_values.get('res.config.settings','is_website_reward')
        website_point=ir_values.get('res.config.settings', 'website_point')
        website_amount_per_point=ir_values.get('res.config.settings', 'website_amount_per_point')
        website_range_from=ir_values.get('res.config.settings', 'website_range_from')
        website_range_to=ir_values.get('res.config.settings', 'website_range_to')
        is_pos_reward = ir_values.get('res.config.settings','is_pos_reward')
        pos_point=ir_values.get('res.config.settings', 'pos_point')
        pos_amount_per_point=ir_values.get('res.config.settings', 'pos_amount_per_point')
        pos_range_from=ir_values.get('res.config.settings', 'pos_range_from')
        pos_range_to=ir_values.get('res.config.settings', 'pos_range_to')
        is_birthday_points=ir_values.get('res.config.settings', 'is_birthday_points')
        birthday_points=ir_values.get('res.config.settings', 'birthday_points')
        earn_point_mini_amount = ir_values.get('res.config.settings','earn_point_mini_amount')
        point_reedem_per_order = ir_values.get('res.config.settings','point_reedem_per_order')
        amount_value_point = ir_values.get('res.config.settings','amount_value_point')
        points_for_amount = ir_values.get('res.config.settings','points_for_amount')
        point_credit_cond = ir_values.get('res.config.settings','point_credit_cond')
        is_send_mail=ir_values.get('res.config.settings','is_send_mail')

        values.update({
            'vip_amount_per_point': vip_amount_per_point,
            'pro_amount_per_point': pro_amount_per_point,
            'ind_amount_per_point': ind_amount_per_point,
            'valid_product_category': valid_product_category,
            'vip_point_duration': vip_point_duration,
            'pro_point_duration': pro_point_duration,
            'ind_point_duration': ind_point_duration,
            'is_website_reward':is_website_reward,
            'website_point':website_point,
            'website_amount_per_point':website_amount_per_point,
            'website_range_from':website_range_from,
            'website_range_to':website_range_to,
            'is_birthday_points':is_birthday_points,
            'birthday_points':birthday_points,
            'is_send_mail':is_send_mail,
            'point_credit_cond':point_credit_cond,
            'points_for_amount':points_for_amount,
            'amount_value_point':amount_value_point,
            'point_reedem_per_order':point_reedem_per_order,
            'earn_point_mini_amount':earn_point_mini_amount
            })
        return values


                

        
    
