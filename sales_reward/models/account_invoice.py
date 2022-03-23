# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountInvoiceRewards(models.Model):

    """Add a new column to the account.invoice model 'Reward Points'"""
    _inherit = 'account.move'
    total_web_points = fields.Float(string="Your Total website Reward Points")
    point_to_use = fields.Integer()
    amount_total_invoice=fields.Float()
    remaining_points=fields.Integer(compute="_compute_remaining_points")
    amount_into_points=fields.Float()
    customer_type_check=fields.Boolean('Check customer type', compute='check_customer_type', default=True)
    amount_of_web_points = fields.Float()
              
                
    @api.onchange('partner_id')
    def _display_rewards_and_redeem(self):    
        settings=self.env['res.partner'].get_setting_values()
        if settings['is_website_reward']:
            self.total_web_points = self.partner_id.total_points
        
        

    @api.onchange('partner_id')
    def check_customer_type(self):
        if(self.partner_id.customer_type=='exp'):
            self.customer_type_check=False
        else:
            self.customer_type_check=True

    def get_partner_type_product(self):
        reward_product=0
        if(self.partner_id.customer_type=='ind'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_ind')])
        elif(self.partner_id.customer_type=='vip'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_vip')])
        elif(self.partner_id.customer_type=='pro'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_pro')])
        return reward_product

    @api.model
    def create(self,vals):
        res = super(AccountInvoiceRewards, self).create(vals)
        settings=self.env['res.partner'].get_setting_values()
     
        if settings['is_website_reward']:
            data = {'total_web_points': res.partner_id.total_points,
                    'point_to_use': res.point_to_use,
                    'amount_into_points':res.amount_into_points
                    }
            res.write(data)
        
        return res

    @api.onchange('point_to_use')
    def _compute_remaining_points(self):

        for obj in self:
            obj.remaining_points =obj.point_to_use



class CustomAccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    point_to_use = fields.Float()


class CustomWebsite(models.Model):
    _name = "sale.reward"
    reward_access_id_ed= fields.Selection([ ('TRUE', 'True'),('FALSE', 'False'),],'Access rewards',default='TRUE')
