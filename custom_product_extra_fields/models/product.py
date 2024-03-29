from odoo import api, fields, models, _
from odoo.http import request
import requests
from odoo.tools.translate import html_translate
import urllib
import base64


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    product_sku = fields.Char("SKU")
    image_url   = fields.Char("Image URL")
    image_image_url = fields.Char("image_image_url 1024")
    
    aw_mfg_part_no  = fields.Char("MFG PART NUMBER")
    # aw_connect_manufacturer = fields.Char("Manufacturer")
    # aw_desc_text = fields.Html('AW Connect Description', sanitize_attributes=False, translate=html_translate, sanitize_form=False)
    
    def product_image_cron(self):
        
        product_ids = self.search([('image_url','!=',False)])
        if product_ids:
            for product_id in product_ids:
                if product_id.image_url and product_id.image_image_url and not product_id.image_1920:
                    product_id.image_1920 = product_id.image_image_url
                    product_id.image_image_url = ""
                    
                        

