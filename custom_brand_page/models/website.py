# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.http import request


class Website(models.Model):

    _inherit = "website"
    
    
    def get_parent_category(self):
        """
        Collect all the parent category. and return with category name and category ID
        @Author : Angel Patel (24/09/2020)
        :return: cat_array
        """
        category_obj = self.env['product.public.category'].sudo().search([('country_website_fitler', '=', False),('website_id','in',[request.env['website'].sudo().get_current_website().id])])
        cat_array = [{'name': "All",'id':""}]
        if category_obj:
            for cat in category_obj:
                cat_array.append({'name': cat.name, 'id': cat.id})
        return cat_array
    
    
    def get_category_brands(self, cat_id=False):
        """
        Collect all the parent category. and return with category name and category ID
        @Author : Angel Patel (24/09/2020)
        :return: cat_array
        """
        domain = []
        if cat_id:
            domain = [('id','=',cat_id)]
            
        category_obj = self.env['product.public.category'].sudo().search(domain+[('country_website_fitler', '=', False),('website_id','in',[request.env['website'].sudo().get_current_website().id])])
        brands = [{'name': "All Brands",'id':""}]
        
        brand_ids = category_obj.mapped('brand_ids')
        
        if brand_ids:
            for brand_id in brand_ids:
                brands.append({'name': brand_id.name, 'id': brand_id.id})
        return brands
    
    def _force_website(self, website_id):
        res = super(Website, self)._force_website(website_id)
        if request:
            request.session['country_filter_id'] = request.session.get('country_filter_id', False)
#     def _force_country_id(self, country_id):
#         self._force_country_website(self.id, country_id)
# 
#     def _force_country_website(self, website_id, country_id):
#         if request:
#             request.session['force_website_id'] = website_id and str(website_id).isdigit() and int(website_id)
#             request.session['country_filter_id'] = country_id.id