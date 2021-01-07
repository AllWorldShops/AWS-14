# -*- coding: utf-8 -*-

from odoo import models, fields, _
import xmlrpc.client

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

import json
import requests
from bs4 import BeautifulSoup
import re
import csv

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"
    
    old_id = fields.Integer("Odoo12 ID")
    
    
class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    public_category_offset = fields.Integer("E-Commerce category Offset")
    public_par_category_offset = fields.Integer("Update e-Commerce parent category Offset")
    
            
    def create_pub_catg(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        category_ids = models.execute_kw(self.db, uid, self.password,'product.public.category', 'search_read',[[]],
                    {'offset': self.public_category_offset, 'limit':10000})
        i = self.public_category_offset
        for category_id in category_ids:
            category_vals  = {
                    'old_id': category_id['id'],
                    'name': category_id['name'],
                    'image_1920': category_id['image'],
                    'sequence': category_id['sequence'],
                }
            pro_pub_id = self.env['product.public.category'].search([('old_id','=',category_id['id'])])
            if pro_pub_id:
                print(pro_pub_id.id)
            else:
                c_category_id = self.env['product.public.category'].create(category_vals)
            i+=1      
            self.public_category_offset = i
            self._cr.commit()  
    
    def create_par_catg(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
                
        categ_ids = models.execute_kw(self.db, uid, self.password,'product.public.category', 'search_read',[[]],{'fields': ['id','parent_id'], 'offset': self.public_par_category_offset,})
        i = self.public_par_category_offset
        for categ_id in categ_ids:
            c_categ_id = self.env['product.public.category'].search([('old_id','=',categ_id['id'])])
            if categ_id['parent_id'] and categ_id['parent_id'][0]:
                c_parent_id = self.env['product.public.category'].search([('old_id','=',categ_id['parent_id'][0])])
                c_categ_id.write({'parent_id': c_parent_id.id})
                i+=1      
                self.public_par_category_offset = i
                self._cr.commit()
    
    
    def Impporttranslationpubliccateg(self):
        
        lang=('en_US', 'zh_CN', 'zh_TW', 'ja_JP', 'ko_KR')
        
        
        with open(self.public_category_path) as csvfile:
            reader = csv.DictReader(csvfile)
            
            count = 0
            for row in list(reader)[self.public_category_offset:]:
                count = count + 1
                
                create = []
                
                if row['en_US']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','en_US'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['en_US']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'en_US',
                                'src' : row['en_US'],
                                'value' : row['en_US'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                
                if row['fr_FR']: 
                    trans2 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','fr_FR'),('res_id','=',row['ID'])], limit=1)
                    if trans2:
                        trans2.value = row['fr_FR']
                    else:
                        trans2_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'fr_FR',
                                'src' : row['en_US'],
                                'value' : row['fr_FR'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['de_DE']: 
                    trans2 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','de_DE'),('res_id','=',row['ID'])], limit=1)
                    if trans2:
                        trans2.value = row['de_DE']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'de_DE',
                                'src' : row['en_US'],
                                'value' : row['de_DE'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['it_IT']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','it_IT'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['it_IT']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'it_IT',
                                'src' : row['en_US'],
                                'value' : row['it_IT'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['tr_TR']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','tr_TR'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['tr_TR']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'tr_TR',
                                'src' : row['en_US'],
                                'value' : row['tr_TR'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['ru_RU']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','ru_RU'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['ru_RU']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'ru_RU',
                                'src' : row['en_US'],
                                'value' : row['ru_RU'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['ro_RO']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','ro_RO'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['ro_RO']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'ro_RO',
                                'src' : row['en_US'],
                                'value' : row['ro_RO'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                if row['es_ES']: 
                    trans1 = self.env['ir.translation'].search([('type','=','model'),('name','=','product.public.category,name'),('lang','=','es_ES'),('res_id','=',row['ID'])], limit=1)
                    if trans1:
                        trans1.value = row['es_ES']
                    else:
                        trans1_vals = self.env['ir.translation'].create({
                                'name' : 'product.public.category,name',
                                'lang' : 'es_ES',
                                'src' : row['en_US'],
                                'value' : row['es_ES'],
                                'type' : 'model',
                                'res_id' : row['ID'],
                                })
                        
                        
                    
                self.public_category_offset = self.public_category_offset+1
                _logger.info("Count : "+str(self.public_category_offset))
                self._cr.commit()
    
                
                
                
        