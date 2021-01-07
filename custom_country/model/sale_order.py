from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    country_id=fields.Many2one('res.country',string='Country',related='partner_id.country_id',store=True)
    
    def get_sale_weight(self):
        total = 0
        for line in self.order_line:
            total = (line.product_id.weight * line.product_uom_qty) + total
        return total