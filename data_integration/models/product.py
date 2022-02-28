# -*- coding: utf-8 -*-

from odoo import api, models, fields,  _
import xmlrpc.client
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import csv

class Product(models.Model):
    _inherit = "product.template"
    
    old_id = fields.Integer("Odoo12 ID")
    
    
class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    product_offset = fields.Integer("Product Offset")
    product_csv_count = fields.Integer("Product count")
    csv_product_path = fields.Char("Product path")
    
    def product_cron(self):
        
        data_integ_id = self.env['data.integration'].search([], limit=1)
        if data_integ_id:
            data_integ_id.create_product()
            
    def update_alternative_accessory_ids(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
                
        product_ids = models.execute_kw(self.db, uid, self.password,'product.template', 'search_read',[[]],{'fields': ['id','alternative_product_ids','accessory_product_ids'], 'offset': self.product_offset,})
        i = self.public_par_category_offset
        for product_id in product_ids:
            c_alternative_ids = []
            c_accessory_ids = []
            c_product_id = self.env['product.template'].search([('old_id','=',product_id['id'])])
            if product_id.get("alternative_product_ids", False):
                c_alternative_ids = self.env['product.template'].search([('old_id','in',product_id.get("alternative_product_ids", False))])
                if c_alternative_ids:
                    c_alternative_ids = c_alternative_ids.ids
            if product_id.get("accessory_product_ids", False):
                c_accessory_ids = self.env['product.template'].search([('old_id','in',product_id.get("accessory_product_ids", False))])
                if c_accessory_ids:
                    c_accessory_ids = c_accessory_ids.ids
            
            if c_accessory_ids or c_alternative_ids:
                c_product_id.write({'alternative_product_ids': c_alternative_ids,'accessory_product_ids':c_accessory_ids})
                
            i+=1      
            self.product_offset = i
            self._cr.commit()        
    
    
    def create_product(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        product_ids = models.execute_kw(self.db, uid, self.password,'product.template', 'search_read',[[]],
                    {'offset': self.product_offset, 'limit':100})
        
#         new_cr = self.pool.cursor()
#         self = self.with_env(self.env(cr=new_cr))
        product_vals = {}
        while product_ids:
            try:
                for product_id in product_ids:
                    product_vals  = {
                            'old_id': product_id.get('id',False),
                            'name':  product_id.get('name',False),
                            'default_code': product_id.get('default_code',False),
                            'image_1920': product_id.get('image',False),
                            'type': product_id.get('type',False),
                            'active': True,
                            'website_published': product_id.get('website_published',False),
                            'weight': product_id.get('weight',False),
                            'standard_price': product_id.get('standard_price',False),
                            'purchase_method': product_id.get('purchase_method',False),
                            'description_sale': product_id.get('description_sale',False),
                            'description_purchase': product_id.get('description_purchase',False),
                            'description_picking': product_id.get('description_picking',False),
                            'invoice_policy': product_id.get('invoice_policy',False),
                            'sale_delay': product_id.get('sale_delay',False),
                            'is_published': product_id.get('is_published',False),
                            'product_nid': product_id.get('product_nid',False),
                            'manufacturers': product_id.get('manufacturers',False),
                            'desc_text': product_id.get('desc_text',False),
                            'sale_ok': product_id.get('sale_ok',False),
                            'supplier_country': product_id.get('supplier_country',False) and self.get_country_by_code(product_id.get('supplier_country',False), models, uid) or False,
                            'old_url': product_id.get('old_url',False),
                            'node_id': product_id.get('node_id',False),
                            'website_description': product_id.get('website_description',False),
                            'hs_code': product_id.get('hs_code',False),
                            'list_price': product_id.get('list_price',False),
                            'website_meta_title': product_id.get('website_meta_title',False),
                            'website_meta_description': product_id.get('website_meta_description',False),
                            'website_meta_keywords': product_id.get('website_meta_keywords',False),
                            'categ_id': product_id.get('categ_id',False) and self.get_categ_id(product_id.get('categ_id',False)) or False,
                            'product_brand_ept_id': product_id.get('product_brand_ept_id',False) and self.get_brand_id(product_id.get('product_brand_ept_id',False)) or False,
                            'public_categ_ids': [(6, 0, product_id.get('public_categ_ids',False) and self.get_public_categ_ids(product_id.get('public_categ_ids',False)) or [])],
                            'taxes_id': [(6, 0, product_id.get('taxes_id',False) and self.get_tax_id(product_id.get('taxes_id',False)) or [])],
                            'supplier_taxes_id': [(6, 0, product_id.get('supplier_taxes_id',False) and self.get_tax_id(product_id.get('supplier_taxes_id',False)) or [])],
    #                         'list_price': product_id.get('list_price',False),
    #                         'list_price': product_id.get('list_price',False),
                            'barcode':product_id.get('barcode',False),
                            
                            
                            }
                    print(product_vals)
                    product = self.env['product.template'].search([("old_id","=", product_id.get('id',False))], limit=1)
                    if product:
                        
                        product.attribute_line_ids.unlink()
                        if product_id.get('attribute_line_ids',False):
                            attribute_ids = self.set_attribute_ids(product_id.get('attribute_line_ids',False), models, uid)
                            product_vals.update({"attribute_line_ids":attribute_ids})
                        
                        product.write(product_vals)
                        
                        if product_id.get('seller_ids',False):
                            product.seller_ids.unlink()
                            self.create_supplier(product, product_id.get('seller_ids',False), models, uid)
                        
                        _logger.info(str(product)+" product Updated successfully.")
                    else:
                        
                        if product_id.get('attribute_line_ids',False):
                            attribute_ids = self.set_attribute_ids(product_id.get('attribute_line_ids',False), models, uid)
                        
                            product_vals.update({"attribute_line_ids":attribute_ids})
                        
                            
                        product = self.env['product.template'].create(product_vals)
                        
                        self.create_supplier(product, product_id.get('seller_ids',False), models, uid)
                        
                        _logger.info(str(product)+" product created successfully.")
                    self.product_offset = self.product_offset+1
                    _logger.info(str(self.product_offset)+" OFFSET.")
                    self._cr.commit()
                    _logger.info(str(product)+" completed process.")
                    
                product_ids = False
                _logger.info(str(self.product_offset)+" OFFSET.")
                product_ids = models.execute_kw(self.db, uid, self.password,'product.template', 'search_read',[[]],
                    {'offset': self.product_offset, 'limit':100})
#                 product_ids = False
            except Exception as e:
                raise UserError(e)
                _logger.info(str(e)+str(product_vals)+" Exception process.")
    
                        
    def create_supplier(self, product_id, seller_ids, models, uid):
        for seller_id in seller_ids:
            seller_id = models.execute_kw(self.db, uid, self.password,'product.supplierinfo', 'search_read',[[('id','=',seller_id)]])
#             if seller_id[0].get('name', False)[0] in (2092,317,311):
    
            if seller_id:
                if self.get_supplier(seller_id[0].get('name',False)):
                    print(seller_id)
                    seller_vals  = {
                            'name':  self.get_supplier(seller_id[0].get('name',False)),
                            'currency_id': 1,
                            'product_code': seller_id[0].get('product_code',False),
                            'product_name': seller_id[0].get('product_name',False),
    #                         'supplier_ref': seller_id[0].get('supplier_ref',False),
                            'price': seller_id[0].get('price',False),
                            'delay': seller_id[0].get('delay',False),
                            'min_qty': seller_id[0].get('min_qty',False),
                            'product_tmpl_id': product_id.id,
                            }
                    
                    seller_id = self.env['product.supplierinfo'].create(seller_vals)
                
    def set_attribute_ids(self, attribute_ids, models, uid):
        p_attr_ids = []
        for attribute_id in attribute_ids:
            attribute_id = models.execute_kw(self.db, uid, self.password,'product.template.attribute.line', 'search_read',[[('id','=',attribute_id)]])
            attri_id = False
            attri_value_ids = []
            if attribute_id:
                attribute_vals  = {
                        }
                
                if attribute_id[0].get("attribute_id", False):
                    attri_id = self.env['product.attribute'].search([('old_id','=',attribute_id[0]['attribute_id'][0])])
                    if attri_id:
                        if attribute_id[0].get("value_ids", False):
                            for a_va_id in attribute_id[0].get("value_ids", False):
                                attri_value_id = []
                                attri_value_id = self.env['product.attribute.value'].search([('attribute_id','=',attri_id.id), ('old_id','in',[a_va_id])])
                                if not attri_value_id:
                                    attri_value_id = models.execute_kw(self.db, uid, self.password,'product.attribute.value', 'search_read',[[('id','=',a_va_id)]])
                                    if attri_value_id:
                                        attri_value_id = self.env['product.attribute.value'].search([('attribute_id','=',attri_id.id), ('name','=',attri_value_id[0]['name'])], limit=1)
                                attri_value_ids = attri_value_ids + [attri_value_id.id]
                        p_attr_ids.append((0, 0, {'attribute_id':attri_id.id,'value_ids' : [(6,0,attri_value_ids)]}))
                        
                        
        return p_attr_ids
                        
                    
    def get_supplier(self, supplier_id):
        if supplier_id:
            supplier_id = self.env['res.partner'].search([('old_id','=',supplier_id[0])], limit=1)
            return supplier_id and supplier_id.id or False
            
        return False
        
            
    def get_product_location_id(self, location_id):
        if location_id[1] == 'WH/Stock':
            location_id = self.env['stock.location'].search([('name','=','Stock')], limit=1)
            return location_id and location_id.id or False
        else:
            location_id = self.env['stock.location'].search([('old_id','=',location_id[0])], limit=1)
            return location_id and location_id.id or False
            
        return False
    
    
    def get_categ_id(self, categ_id):
        if categ_id:
            categ_id = self.env['product.category'].search([('old_id','=',categ_id[0])], limit=1)
            return categ_id and categ_id.id or 1
            
        return False
    
    def get_brand_id(self, brand_id):
        if brand_id:
            categ_id = self.env['product.brand.ept'].search([('old_id','=',brand_id[0])], limit=1)
            return categ_id and categ_id.id or False
            
        return False
    
    def get_public_categ_ids(self, public_categ_ids):
        public_categ_ids = self.env['product.public.category'].search([('old_id','in',public_categ_ids)])
#         print(public_categ_ids)
        return public_categ_ids and public_categ_ids.ids or []
    
    def get_tax_id(self, tax_id):
        if tax_id:
            tax_id = self.env['account.tax'].search([('old_id','in',tax_id)], limit=1)
            return tax_id and tax_id.ids or False
        
        return False
    
    
    def get_country_by_code(self, country_id, models, uid):
        country_id = models.execute_kw(self.db, uid, self.password,'res.country', 'search_read',[[('id','=',country_id[0])]])
        if country_id:
            country_id = self.env['res.country'].search([('code','=',country_id[0]['code'])], limit=1)
            if country_id:
                return country_id.id
            
        return False
    
    
    
    def csv_prduct_import(self, id=None):
        company_id = 5
        if id:
            data_integ_id = self.env['data.integration'].browse(id)
            data_integ_id.create_csv_prduct(company_id)
            
            
    def create_csv_prduct(self, company_id):
        product_csv_count = self.product_csv_count 
        if product_csv_count < 0:
            product_csv_count = 0
            
        with open(self.csv_product_path) as csvfile:
            reader = csv.DictReader(csvfile)
            
            product_ref = []
            count = 0
            
            for row in list(reader)[product_csv_count:]:
                _logger.info("Product Count : "+str(self.product_csv_count))
                
                
                product_id  = self.env['product.template'].search([('default_code', '=', row.get('Internal Reference', ''))])
                if not product_id:
                    categ_id = self.env['product.category'].search([('name','=',row.get('Product Category', ''))], limit=1)
                    public_categ_id = self.env['product.public.category'].search([('name','=',row.get('Product Category', ''))], limit=1)
                    
                    if categ_id:
                        categ_id = categ_id.id
                    else:
                        categ_id = self.create_categ(row.get('Product Category', ''), 'product.category').id
                        
                    if public_categ_id:
                        public_categ_id = public_categ_id
                    else:
                        public_categ_id = self.create_categ(row.get('Product Category', ''), 'product.public.category')
                    
                        
                    product_vals = {
                            'name':row.get('Name', ''),
                            'default_code': row.get('Internal Reference', ''),
                            'categ_id':categ_id,
                            'type': 'product',
                            'active': True,
                            'aw_mfg_part_no':row.get('aw_mfg_part_no', ''),
                            'desc_text':row.get('Description', ''),
                            'public_categ_ids': [(6,0,public_categ_id.ids)],
                            'company_id': company_id,
                            'manufacturers': row.get('Manufacturer', ''),
                        }
                    product = self.env['product.template'].create(product_vals)
                    
                    
                self.product_csv_count = self.product_csv_count+1
                                
                self._cr.commit()
                    
                    
    def create_categ(self, name, model):
                
        categ_id = self.env[model].create({
                    'name' : name,
                    })
        
        self._cr.commit()
        
        return categ_id
    
    
    
    
    
    
    
    
    
    
    
            
