from odoo import api, fields, models, _
from odoo.http import request
import requests
from odoo.tools.translate import html_translate
import base64
import urllib
import os
os.environ["PYTHONHTTPSVERIFY"] = "0"
import ssl
ssl._create_default_https_context = ssl._create_unverified_context




class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    product_sku = fields.Char("SKU")
    image_url   = fields.Char("Image URL")
    
    def product_image_cron(self):
        
        product_ids = self.search([('image_url','!=',False)])
        print(len(product_ids))
        if product_ids:
            for product_id in product_ids:
                if product_id.image_url:
                    context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    image_medium = base64.encodebytes(urllib.request.urlopen(product_id.image_url, context=ssl._create_unverified_contex()).read())
                    if image_medium:
                        product_id.image_1920 = image_medium

