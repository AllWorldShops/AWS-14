# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ast import literal_eval
from enum import Enum


class RewardPointsSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    """Two sales channel"""
    is_pos_reward=fields.Boolean(string="POS sales", default=True)
    is_website_reward=fields.Boolean(string="Website sales", default=True)
    """Client price per point"""
    vip_amount_per_point=fields.Monetary(default=0,string="VIP point")
    pro_amount_per_point=fields.Monetary(default=0,string="Professional point")
    ind_amount_per_point=fields.Monetary(default=0,string="Individual point")
    """Client point time duration"""
    vip_point_duration=fields.Integer(string="Validity of VIP point", default=0)
    pro_point_duration=fields.Integer(string="Validity of Professional point", default=0)
    ind_point_duration=fields.Integer(string="Validity of Individual point", default=0)
    valid_product_category = fields.Many2many('product.category', string="Product Category")

    """POS Price range"""
    pos_range_from=fields.Integer(string="From")
    pos_range_to=fields.Char(string="To")
    """Points add per POS sale and its amount"""
    pos_point=fields.Integer(string="Reward Points")
    pos_amount_per_point=fields.Monetary(string="Price of one point")
    """Website settings"""
    website_range_from=fields.Integer(string="From")
    website_range_to=fields.Char(string="To")
    """Points add per website sale and its amount"""
    website_point=fields.Integer(string="Reward Points")
    website_amount_per_point=fields.Monetary(string="Price of one point", default=0)
    """ Birthday points and  there amount"""
    is_birthday_points=fields.Boolean(string="Set birthday point")
    birthday_points= fields.Float('Birthday Points')
    amount_per_birthday_point=fields.Monetary('Price of one point')

    is_send_mail=fields.Boolean('Send Email')
    earn_point_mini_amount = fields.Monetary(string="Minimum Amount ", default=0)
    point_reedem_per_order = fields.Integer(string="Maximum Points Redeem per order",default=0)
    amount_value_point = fields.Monetary(string="Amount value for point", default=0)
    points_for_amount = fields.Integer(string="Points",default=0)
    point_credit_cond = fields.Selection([('confirm', 'On Payment'),('complete', 'On Delivery')],string="Point Credit Condition")

    def execute(self):
        res=super(RewardPointsSettings,self).execute()
        ir_values = self.env['ir.default']
        ir_values.set('res.config.settings','vip_amount_per_point',self.vip_amount_per_point)
        ir_values.set('res.config.settings','pro_amount_per_point',self.pro_amount_per_point)
        ir_values.set('res.config.settings','ind_amount_per_point',self.ind_amount_per_point)
        ir_values.set('res.config.settings','vip_point_duration',self.vip_point_duration)
        ir_values.set('res.config.settings','pro_point_duration',self.pro_point_duration)
        ir_values.set('res.config.settings','ind_point_duration',self.ind_point_duration)
        ir_values.set('res.config.settings','valid_product_category',self.valid_product_category.ids)
        ir_values.set('res.config.settings','earn_point_mini_amount',self.earn_point_mini_amount)
        ir_values.set('res.config.settings','point_reedem_per_order',self.point_reedem_per_order)
        ir_values.set('res.config.settings','amount_value_point',self.amount_value_point)
        ir_values.set('res.config.settings','points_for_amount',self.points_for_amount)
        ir_values.set('res.config.settings','point_credit_cond',self.point_credit_cond)
        if(self.vip_amount_per_point):
            self.env['product.product'].search([('default_code','=','reward_vip')]).update({'list_price':-self.vip_amount_per_point})
        if(self.pro_amount_per_point):
            self.env['product.product'].search([('default_code','=','reward_pro')]).update({'list_price':-self.pro_amount_per_point})
        if(self.ind_amount_per_point):
            self.env['product.product'].search([('default_code','=','reward_ind')]).update({'list_price':-self.ind_amount_per_point})

        if self.is_pos_reward:
            ir_values.set('res.config.settings', 'pos_range_from', self.pos_range_from)
            ir_values.set('res.config.settings', 'pos_range_to', self.pos_range_to)
            ir_values.set('res.config.settings', 'pos_point', self.pos_point)
            ir_values.set('res.config.settings', 'pos_amount_per_point', self.pos_amount_per_point)

        if self.is_website_reward:

            ir_values.set('res.config.settings', 'website_range_from', self.website_range_from)
            ir_values.set('res.config.settings', 'website_range_to', self.website_range_to)
            ir_values.set('res.config.settings', 'website_point', self.website_point)
            ir_values.set('res.config.settings', 'website_amount_per_point', self.website_amount_per_point)

        if self.is_birthday_points:

            ir_values.set('res.config.settings', 'birthday_points', self.birthday_points)
            ir_values.set('res.config.settings', 'amount_per_birthday_point', self.amount_per_birthday_point)

        ir_values.set('res.config.settings','is_pos_reward',self.is_pos_reward)
        ir_values.set('res.config.settings','is_website_reward',self.is_website_reward)
        ir_values.set('res.config.settings','is_birthday_points',self.is_birthday_points)
        ir_values.set('res.config.settings','is_send_mail',self.is_send_mail)

class ProductCategoryCustom(models.Model):
    _inherit = "website"
    reward_access_id= fields.Selection([ ('TRUE', 'True'),('FALSE', 'False'),],'Access rewards', default='TRUE')

















