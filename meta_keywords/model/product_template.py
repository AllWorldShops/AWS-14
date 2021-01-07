from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class Productemplate(models.Model):
    _inherit='product.template'
    
    website_meta_title=fields.Char(string="Meta Title")
    website_meta_description=fields.Text(string="Meta Description")
    website_meta_keywords=fields.Char(string="Meta Keywords")
    
class ProducProduct(models.Model):
    _inherit='product.product'
    
    website_meta_title=fields.Char(string="Meta Title", related='product_tmpl_id.website_meta_title', store=True, readonly=False)
    website_meta_description=fields.Text(string="Meta Description", related='product_tmpl_id.website_meta_description', store=True, readonly=False)
    website_meta_keywords=fields.Char(string="Meta Keywords", related='product_tmpl_id.website_meta_keywords', store=True, readonly=False)
   