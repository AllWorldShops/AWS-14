from odoo import api, fields, models, _
from odoo.http import request
import requests
from odoo.tools.translate import html_translate




class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    product_sku = fields.Char("SKU")
    

