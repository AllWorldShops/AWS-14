from odoo import api, fields, models, _
from odoo.http import request
import requests


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    manunfacturer_code=fields.Char(string="Manufacturer Code")
    payment_type=fields.Char(string="Payment Type")
    balance_date=fields.Date(string="Balance Date")
    credit_limit=fields.Float(string="Credit Limit")
    email2=fields.Char(string="Email2")
    phone2=fields.Char(string="Phone2")
   