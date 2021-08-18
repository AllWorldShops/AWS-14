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
    image_image_url = fields.Binary("image_image_url 1024")
    
    def product_image_cron(self):
        
        product_ids = self.search([('image_url','!=',False)], limit=1)
        if product_ids:
            for product_id in product_ids:
                print(product_id)
                if product_id.image_url:
                    response = requests.get(product_id.image_url, stream = True, verify=False)
                    if response.status_code == 200:
                        response.raw.decode_content = True
                        image_medium = base64.encodebytes(response.content)
                    if image_medium:
                        product_id.image_1920 = image_medium
                        

