from odoo import api, fields, models, _
from odoo.http import request
import requests
from odoo.tools.translate import html_translate
import re


class ProductProduct(models.Model):
    _inherit = 'product.product'

    website_description = fields.Html('Description for the website', sanitize_attributes=False, sanitize=False, translate=True)
    
#     @api.multi
    def cron_product_updates(self):
        temp_open_ids = self.env['product.product'].search([])
        for rec in temp_open_ids:
            if rec:
                rec.website_description = rec.mag_description
                rec.description_sale = rec.mag_short_description
                
    def cron_product_variant_remove_updates(self):  
        product_tmpl_ids = self.env['product.template'].search([],offset=0)
        if product_tmpl_ids:
            for product_tmpl_id in product_tmpl_ids:
                try:
#                     product_tmpl_id.categ_id = False
                    product_tmpl_id.public_categ_ids = [(6, 0, [])]
                    product_tmpl_id.attribute_line_ids.unlink()
                    self.env.cr.commit()
                except Exception as e:
                    print(e, "An exception occurred")

#     @api.multi
    def cron_product_state_updates(self):

        product_attribute_details = self.env['product.attribute.detail'].search([('market_pl.attribute_code', '=', 'status'), ('market_ch.value', '=', 1)])

        product_templates = []
        product_products = []

        for product in product_attribute_details:
            product_templates.append(product.magento_product.product_tmpl_id.id)
            product_products.append(product.magento_product.id)

        query = """update product_template set active = true, is_published = true where id in %s"""
        self._cr.execute(query, [tuple(product_templates)])

        query = """update product_template set active = false, is_published = false where id not in %s"""
        self._cr.execute(query, [tuple(product_templates)])

        query = """update product_product set active = true where id in %s"""
        self._cr.execute(query, [tuple(product_products)])

        query = """update product_product set active = false where id not in %s"""
        self._cr.execute(query, [tuple(product_products)])

#     @api.multi
    def cron_update_website_categories(self):

        product_products = self.env['product.product'].search([])
        # product_products = self.env['product.product'].browse(8671)

        for product in product_products:
            print(product)
            for category in product.prods_cat_id:
                print(category.name.name)
                print(category.name.parent_id.name)
                if category.name.parent_id:
                    public_category = self.env['product.public.category'].search([('name', '=', category.name.name), ('parent_id.name', '=', category.name.parent_id.name)])
                else:
                    public_category = self.env['product.public.category'].search([('name', '=', category.name.name)])
                if len(public_category) > 1:
                    i = 0
                    for cat in public_category:
                        if i > 0:
                            update_parents = self.env['product.public.category'].search([('parent_id', '=', category.name.parent_id.id)])
                            if update_parents:
                                update_parents.parent_id = category.name.parent_id.id
                            cat.unlink()
                        i += 1
                    if category.name.parent_id:
                        public_category = self.env['product.public.category'].search([('name', '=', category.name.name), ('parent_id.name', '=', category.name.parent_id.name)])
                    else:
                        public_category = self.env['product.public.category'].search([('name', '=', category.name.name)])
                        
                if public_category:
                    product.public_categ_ids = [(4, public_category.id)]
                else:
                    stop

#     @api.multi
    def cron_update_product_weight(self):
        products = self.env['product.attribute.detail'].search([('market_pl.attribute_code', '=', 'weight')])
        for line in products:
            if line.magento_product:
                line.magento_product.weight = line.market_ch.value


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    supplier_country = fields.Many2one('res.country', string="Supplier Country")
    old_url = fields.Char("Old-URL")
    node_id = fields.Char("Node ID")
    website_description = fields.Html('Description for the website', sanitize_attributes=False, sanitize=False, translate=True)
    website_country_id = fields.Many2one("product.public.category", string="Website Country")
    
    def cron_product_website_html_tags(self):
        products_ids = self.search([('description_sale','!=',False)])
        TAG_RE = re.compile(r'<[^>]+>')
        if products_ids:
            for products_id in products_ids:
                description_sale = TAG_RE.sub('', products_id.description_sale)
                products_id.description_sale = description_sale.replace('&nbsp;', ' ')
                products_id.env.cr.commit()
    
#     @api.multi
    def cron_product_website_updates(self):  
        product_open_ids = self.env['product.product'].search([('magento_exported', '=', True)])
        if product_open_ids:
            for value in product_open_ids:
                try:
                    value.product_tmpl_id.website_description = value.mag_description
                except Exception:
                    print(value, "An exception occurred")


# // Product Weight info message
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    product_message = fields.Html(string="Dynamic Product Weight Info message", store=True)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        obj = (ICPSudo.get_param('custom_product.product_message'))
        res.update(
            product_message=obj
        )
        return res

#     @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("custom_product.product_message", self.product_message)

        
class Website(models.Model):
    _inherit = "website"
    
#     @api.multi 
    def dynamic_product_message(self):
        product_message = request.env['ir.config_parameter'].sudo().get_param('custom_product.product_message')
        if product_message:
            return product_message
        else:
            False
