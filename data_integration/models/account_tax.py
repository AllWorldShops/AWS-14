# -*- coding: utf-8 -*-

from odoo import api, models, fields,  _
import xmlrpc.client

class AccountTax(models.Model):
    _inherit = "account.tax"
    
    old_id = fields.Integer("Odoo12 ID")

class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    tax_offset = fields.Integer("Tax Offset")
    
    def create_tax(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        tax_ids = models.execute_kw(self.db, uid, self.password,'account.tax', 'search_read',[[]],
                    {'fields': ['id', 'name', 'active', 'amount', 'amount_type', 'description', 'type_tax_use','analytic','price_include','tax_group_id','account_id','refund_account_id','include_base_amount'], 'offset': self.tax_offset,})
        i = self.tax_offset
        for tax_id in tax_ids:
            tax_vals  = {
                    'old_id': tax_id['id'],
                    'name': tax_id['name'],
                    'active': tax_id['active'],
                    'amount': tax_id['amount'],
                    'amount_type': tax_id['amount_type'],
                    'description': tax_id['description'],
                    'type_tax_use': tax_id['type_tax_use'],
                    'analytic': tax_id['analytic'],
                    'price_include': tax_id['price_include'],
                    'include_base_amount': tax_id['include_base_amount'],
                    }
            taxes_id = self.env['account.tax'].search([('name','=',tax_id['name']),('type_tax_use','=',tax_id['type_tax_use'])], limit=1)
            if not taxes_id:
                taxes_id = self.env['account.tax'].search([('old_id','=',tax_id['id'])], limit=1)
            if taxes_id:
                taxes_id.write(tax_vals)
                if tax_id['tax_group_id']:
                    taxes_id.write({'tax_group_id': 1})
            else:
                taxes_id = self.env['account.tax'].create(tax_vals)
                if tax_id['tax_group_id']:
                    taxes_id.write({'tax_group_id': 1})
            i+=1      
            self.tax_offset = i
            self._cr.commit()  
