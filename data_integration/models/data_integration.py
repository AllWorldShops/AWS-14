# -*- coding: utf-8 -*-

from odoo import models, fields, _
import xmlrpc.client

import logging
_logger = logging.getLogger(__name__)

class DataIntegration(models.Model):
    _name = "data.integration"
    _description = 'Data Integration'
    _rec_name = 'url'
    
    url = fields.Char("URL")
    db = fields.Char("Database")
    username = fields.Char("User name")
    password = fields.Char("Password")   
    
    def get_many2one_id(self, models, db, uid, password, model, val):
        rec = models.execute_kw(db, uid, password, model, 'search_read', [[('id', '=', val)]],{'limit': 1}) 
        if not rec:
            rec = models.execute_kw(db, uid, password, model, 'search_read', [['|',('active', '=', True),('active', '=', False),('id', '=', val)]],{'limit': 1})
        return self.env[model].search([('old_id', '=', rec[0]['id'])],limit=1).id if rec else False
    
    def get_taxes_ids(self, tax_ids):
        if tax_ids:
            tax_id = self.env['account.tax'].search([('old_id','in',tax_ids)])
            return tax_id.ids or []
        
    def get_many_ids(self, model, many_ids):
        if many_ids:
            many_id = self.env[model].search([('old_id','in',many_ids)])
            return many_id.ids or []
            self._cr.commit()
            
            
    
# class AnalyticTag(models.Model):
#     _inherit = "account.analytic.tag"
#     
#     old_id = fields.Integer("Odoo10 ID")
    
# class PartnerTitle(models.Model):
#     _inherit = "res.partner.title"
#     
#     old_id = fields.Integer("Odoo10 ID")
    
# class PartnerCategory(models.Model):
#     _inherit = "res.partner.category"
#     
#     old_id = fields.Integer("Odoo10 ID")
    
# class AccountIncoterms(models.Model):
#     _inherit = "account.incoterms"
#     
#     old_id = fields.Integer("Odoo10 ID")
#     
class UomUom(models.Model):
    _inherit = "uom.uom"
    
    old_id = fields.Integer("Odoo10 ID")
    
# class CrmTeam(models.Model):
#     _inherit = "crm.team"
#     
#     old_id = fields.Integer("Odoo10 ID")
    
# class CountryGroup(models.Model):
#     _inherit = "res.country.group"
#     
#     old_id = fields.Integer("Odoo10 ID")


class ResCountry(models.Model):
    _inherit = 'res.country'

    def get_website_sale_countries(self, mode='billing'):
        res = super(ResCountry, self).get_website_sale_countries(mode=mode)
        if mode == 'shipping' and self.env.company.id != 5:
            countries = self.env['res.country']
            delivery_carriers = self.env['delivery.carrier'].sudo().search([('website_published', '=', True)])
            for carrier in delivery_carriers:
                if not carrier.country_ids and not carrier.state_ids:
                    countries = res
                    break
                countries |= carrier.country_ids

            res = res & countries
        if mode == 'shipping' and self.env.company.id == 5:
            countries = self.env['res.country'].search([])
            res = countries    
        return res