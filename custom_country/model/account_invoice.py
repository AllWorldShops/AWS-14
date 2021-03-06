from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit='account.invoice'
    
    country_id=fields.Many2one('res.country',string='Country',related='partner_id.country_id',store=True)
    
