# -*- coding: utf-8 -*-

from odoo import api, models, fields,  _
import xmlrpc.client
import re
import logging
_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    old_id = fields.Integer("Odoo12 ID")
    
#     Remove duplicate category from odoo14

class Productattribute(models.Model):
    _inherit = "product.attribute"
    
    old_id = fields.Integer("Odoo12 ID")
    
class Productattributevalue(models.Model):
    _inherit = "product.attribute.value"
    
    old_id = fields.Integer("Odoo12 ID")
    
class Productbrand(models.Model):
    _inherit = "product.brand.ept"
    
    old_id = fields.Integer("Odoo12 ID")
    
    
    
    
class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    product_category_offset = fields.Integer("Product category Offset")
    product_attribute_offset = fields.Integer("Product Attribute Offset") 
    product_brand_offset = fields.Integer("Product Brand Offset") 
    
    def create_pro_attribute(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        product_attribute_ids = models.execute_kw(self.db, uid, self.password,'product.attribute', 'search_read',[[]],
                    {'offset': self.product_attribute_offset,})
        
        i = self.product_attribute_offset
        for attribute_id in product_attribute_ids:
            attribute_vals  = {
                    'old_id': attribute_id['id'],
                    'name': attribute_id['name'],
                    'display_type': attribute_id.get('type', False),
                    'create_variant': attribute_id.get('create_variant', False),   
                    'is_quick_filter': attribute_id.get('is_quick_filter', False),                                      
                    }
            cat_id = self.env['product.attribute'].search(['|',('old_id','=',attribute_id['id']),('name','=',attribute_id['name'])])
            if cat_id:
                cat_id.write(attribute_vals)
                
                if attribute_id.get("category_id", False):
                    category_id = self.env['product.attribute.category'].search([('name','=',attribute_id['category_id'][1])], limit=1)
                    if not category_id:
                        attribute_category_vals  = {
                            'name': attribute_id['category_id'][1],
                            }
                        category_id = self.env['product.attribute.category'].create(attribute_category_vals)
                        
                    cat_id.write({'category_id': category_id.id})
                    
                    
                if attribute_id.get("value_ids", False):
                    for value_id in attribute_id.get("value_ids", False):
                        value_id = models.execute_kw(self.db, uid, self.password,'product.attribute.value', 'search_read',[[('id','=',value_id)]])
                        value_vals  = {
                                'old_id': value_id[0]['id'],
                                'name':  value_id[0].get('name',False),
                                'is_custom': value_id[0].get('is_custom',False),
                                'html_color': value_id[0].get('html_color',False),
                                'attribute_id': cat_id.id,
                                }
                        c_value_id = self.env['product.attribute.value'].search([('attribute_id','=',cat_id.id),('name','=',value_id[0].get('name',False))], limit=1)
                        if c_value_id:
                            c_value_id.write(value_vals)
                        else:
                            self.env['product.attribute.value'].create(value_vals)
                    
            else:
                c_attribute_id = self.env['product.attribute'].create(attribute_vals)
                
                if attribute_id.get("category_id", False):
                    category_id = self.env['product.attribute.category'].search([('name','=',attribute_id['category_id'][1])], limit=1)
                    if not category_id:
                        attribute_category_vals  = {
                            'name': attribute_id['category_id'][1],
                            }
                        category_id = self.env['product.attribute.category'].create(attribute_category_vals)
                        
                    c_attribute_id.write({'category_id': category_id.id})
                    
                    
                if attribute_id.get("value_ids", False):
                    for value_id in attribute_id.get("value_ids", False):
                        value_id = models.execute_kw(self.db, uid, self.password,'product.attribute.value', 'search_read',[[('id','=',value_id)]])
                        value_vals  = {
                                'old_id': value_id[0]['id'],
                                'name':  value_id[0].get('name',False),
                                'is_custom': value_id[0].get('is_custom',False),
                                'html_color': value_id[0].get('html_color',False),
                                'attribute_id': c_attribute_id.id,
                                }
#                         c_value_id = self.env['product.attribute.value'].search([('name','=',value_id[0].get('name',False))], limit=1)
#                         if c_value_id:
#                             c_value_id
                        
                        self.env['product.attribute.value'].create(value_vals)
                
            i+=1      
            self.product_attribute_offset = i
            self._cr.commit()  
            
            
    def create_pro_catg(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        product_category_ids = models.execute_kw(self.db, uid, self.password,'product.category', 'search_read',[[]],
                    {'fields': ['id','name','parent_id','property_cost_method','property_valuation','property_account_income_categ_id',
                                'property_account_creditor_price_difference_categ','property_account_income_categ_id','property_account_expense_categ_id',
                                'property_stock_account_input_categ_id','property_stock_account_output_categ_id','property_stock_valuation_account_id',
                                'property_stock_journal'], 'offset': self.product_category_offset,})
        i = self.product_category_offset
        for category_id in product_category_ids:
            category_vals  = {
                    'old_id': category_id['id'],
                    'name': category_id['name'],
                    'property_cost_method': category_id['property_cost_method'],
                    'property_valuation': category_id['property_valuation'],                                      
                    }
            cat_id = self.env['product.category'].search(['|',('old_id','=',category_id['id']),('name','=',category_id['name'])])
            if cat_id:
                cat_id.write(category_vals)
                if category_id['property_account_creditor_price_difference_categ']:
                    new_credtior_id = self.env['account.account'].search([('old_id','=',category_id['property_account_creditor_price_difference_categ'][0])])
                    cat_id.write({'property_account_creditor_price_difference_categ': new_credtior_id.id})
                if category_id['property_account_income_categ_id']:
                    new_income_id = self.env['account.account'].search([('old_id','=',category_id['property_account_income_categ_id'][0])])
                    cat_id.write({'property_account_income_categ_id': new_income_id.id})
                if category_id['property_account_expense_categ_id']:
                    new_expense_id = self.env['account.account'].search([('old_id','=',category_id['property_account_expense_categ_id'][0])])
                    cat_id.write({'property_account_expense_categ_id': new_expense_id.id})
                if category_id['property_stock_account_input_categ_id']:
                    new_input_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_account_input_categ_id'][0])])
                    cat_id.write({'property_stock_account_input_categ_id': new_input_id.id})
                if category_id['property_stock_account_output_categ_id']:
                    new_output_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_account_output_categ_id'][0])])
                    cat_id.write({'property_stock_account_output_categ_id': new_output_id.id})
                if category_id['property_stock_valuation_account_id']:
                    new_val_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_valuation_account_id'][0])])
                    cat_id.write({'property_stock_valuation_account_id': new_val_id.id})
                if category_id['parent_id']:
                    new_val_id = self.env['product.category'].search([('old_id','=',category_id['parent_id'][0])])
                    cat_id.write({'parent_id': new_val_id.id})
#                 if category_id['property_stock_journal']:
#                     new_journal_id = self.env['account.journal'].search([('old_id','=',category_id['property_stock_journal'][0])])
#                     cat_id.write({'property_stock_journal': new_journal_id.id})
            else:
                c_category_id = self.env['product.category'].create(category_vals)
                if category_id['property_account_creditor_price_difference_categ']:
                    new_credtior_id = self.env['account.account'].search([('old_id','=',category_id['property_account_creditor_price_difference_categ'][0])])
                    c_category_id.write({'property_account_creditor_price_difference_categ': new_credtior_id.id})
                if category_id['property_account_income_categ_id']:
                    new_income_id = self.env['account.account'].search([('old_id','=',category_id['property_account_income_categ_id'][0])])
                    c_category_id.write({'property_account_income_categ_id': new_income_id.id})
                if category_id['property_account_expense_categ_id']:
                    new_expense_id = self.env['account.account'].search([('old_id','=',category_id['property_account_expense_categ_id'][0])])
                    c_category_id.write({'property_account_expense_categ_id': new_expense_id.id})
                if category_id['property_stock_account_input_categ_id']:
                    new_input_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_account_input_categ_id'][0])])
                    c_category_id.write({'property_stock_account_input_categ_id': new_input_id.id})
                if category_id['property_stock_account_output_categ_id']:
                    new_output_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_account_output_categ_id'][0])])
                    c_category_id.write({'property_stock_account_output_categ_id': new_output_id.id})
                if category_id['property_stock_valuation_account_id']:
                    new_val_id = self.env['account.account'].search([('old_id','=',category_id['property_stock_valuation_account_id'][0])])
                    c_category_id.write({'property_stock_valuation_account_id': new_val_id.id})
                if category_id['parent_id']:
                    new_val_id = self.env['product.category'].search([('old_id','=',category_id['parent_id'][0])])
                    c_category_id.write({'parent_id': new_val_id.id})
                
#                 if category_id['property_stock_journal']:
#                     new_journal_id = self.env['account.journal'].search([('old_id','=',category_id['property_stock_journal'][0])])
#                     c_category_id.write({'property_stock_journal': new_journal_id.id})
            i+=1      
            self.product_category_offset = i
            self._cr.commit() 
            
            
    def import_brand_to_odoo14(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        product_brand_ids = models.execute_kw(self.db, uid, self.password,'product.brand.ept', 'search_read',[[]],
                    {'offset': self.product_brand_offset,})
        i = self.product_brand_offset
        for brand_id in product_brand_ids:
            brand_vals  = {
                    'old_id': brand_id['id'],
                    'name': brand_id['name'],
                    'logo': brand_id.get("logo", False),
                    'description': brand_id.get("description", False),   
                    'website_published': brand_id.get('website_published',False),                                   
                    }
            cat_id = self.env['product.brand.ept'].search(['|',('old_id','=',brand_id['id']),('name','=',brand_id['name'])])
            if cat_id:
                cat_id.write(brand_vals)
            else:
                c_brand_id = self.env['product.brand.ept'].create(brand_vals)
            i+=1      
            self.product_brand_offset = i
            self._cr.commit()  
            
