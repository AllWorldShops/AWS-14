# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


# // Inherits users
class Users(models.Model):
    _inherit = "res.users"

    user_aid = fields.Char('User aid', help="This field gets the value when the data is imported from the csv file using Users Import.")
    user_uid = fields.Char('User uid', help="This field gets the value when the data is imported from the csv file using Users Import.")

#     @api.multi
    def cron_send_invitation_mail(self):
        users = self.env['res.users'].search([('state', '=', 'new')])
        for user in users:
            user.action_reset_password()

    @api.model
    def _update_last_login(self):
        
        res = super(Users, self)._update_last_login()
        
        if self.state == 'active':
            self.partner_id.sudo().write({'subscribed_login':True})
        
        return res


# // Inherits Partners
class Partner(models.Model):
    _inherit = "res.partner"

    partner_aid = fields.Char('Partner aid', help="This field gets the value when the data is imported from the csv file using Users Import.")
    partner_uid = fields.Char('Partner uid', help="This field gets the value when the data is imported from the csv file using Users Import.")
    gender = fields.Selection([('select', 'Select the Gender'), ('male', 'Male'), ('female', 'Female')], "Gender", default='select')    
    exported_country_code = fields.Char("Exported Country Code", help="This field gets the value when the country is exported from the magento database.")
    subscribed_login = fields.Boolean("Subscribed", help="Checks only if the user logged in for the first time.")

    
# // Inherits Sales Reward
# class RewardExpire(models.Model):
#     _inherit = "reward.expire"
# 
#     reward_id = fields.Char(string="Reward aid", help="This field gets it's value based on data import for rewards.")
#     reward_uid = fields.Char(string="Reward uid", help="This field gets it's value based on data import for rewards.")


# // Inherits Products
class Product(models.Model):
    _inherit = "product.template"

    product_nid = fields.Char('Partner nid', help="This field gets the value when the data is imported from the csv file.")
    manufacturers = fields.Char('Manufacturer', help="This field gets the value when the data is imported from the csv file.")
    desc_text = fields.Text("Directions",translate=True)
