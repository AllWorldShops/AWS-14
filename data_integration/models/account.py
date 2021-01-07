# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import xmlrpc.client
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

# Currency
# Taxes


# url = "http://192.168.1.21:8069"
# db = "enoa_10"
# username = "denis.pasquier@enoa-sas.com"
# password = ":StA\>7XSu)VZ;"q"

class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    account_offset = fields.Integer("Chart Of Account Offset")
    
    def account_creation(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        account_ids = models.execute_kw(self.db, uid, self.password,'account.account', 'search_read',[[]], {'offset': self.account_offset})
        for account_id in account_ids:
            print(account_id)
            account_vals  = {
                    'old_id': account_id.get('id',False),
                    'code': account_id.get('code',False),
                    'name': account_id.get('name',False),
#                     'active': account_id.get('active',False),
                    'tax_ids': [(6, 0, account_id.get('tax_ids',False) and self.get_taxes(account_id.get('tax_ids',False)) or [])],
                    'currency_id': account_id.get('currency_id',False) and self.get_currency_id(account_id.get('currency_id',False)[0]) or False,
                    'reconcile': account_id.get('reconcile',False),
                    'deprecated': account_id.get('deprecated',False),
#                     'compacted': account_id.get('compacted',False),
#                     'type_third_parties': account_id.get('type_third_parties',False),
                    'user_type_id': account_id.get('user_type_id',False) and self.get_user_type_id(account_id.get('user_type_id',False)[1]) or False,
                    }
            print(account_vals)
            account = self.env['account.account'].search([("code","=", account_id.get('code',False))], limit=1)
            if account:
                account.write(account_vals)
                _logger.info(str(account)+" Account Updated successfully.")
            else:
                account = self.env['account.account'].create(account_vals)
                _logger.info(str(account)+" Account created successfully.")
            self.account_offset = self.account_offset+1
            self._cr.commit()
            _logger.info(str(account)+" completed process.")
            
    def get_taxes(self, tax_ids):
        tax_ids = self.env['account.tax'].search([('old_id','in',tax_ids)])
        return tax_ids and tax_ids.ids or []
    
    def get_currency_id(self, currency_id):
        currency_id = self.env['res.currency'].search([('old_id','=',currency_id)], limit=1)
        return currency_id and currency_id.id or False
    
    def get_user_type_id(self, user_type_id):
        user_type_id = self.env['account.account.type'].search([('name','=',user_type_id)], limit=1)
        return user_type_id and user_type_id.id or False
            

class Account(models.Model):
    _inherit = "account.account"
    
    old_id = fields.Integer(string="odoo12 ID")
    
    