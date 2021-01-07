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


class product_translation(models.Model):
    _inherit = "data.integration"
    
    
    def import_product_translation_cron(self):
        data_integ_id = self.env['data.integration'].search([], limit=1)
        if data_integ_id:
            data_integ_id.import_product_translation()

        
    def import_product_translation(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
        langs = ['en_US','zh_CN','zh_TW','ja_JP','ko_KR']
        
        i = self.product_offset
        
        product_ids = self.env['product.template'].search([], offset=self.product_offset)
        
        for product_id in product_ids:
            
            for lang in langs:
                import_product_id = models.execute_kw(self.db, uid, self.password,'ir.translation', 'search_read',[[['lang','=',lang],['name','=','product.template,name'],['res_id','=',product_id.old_id]]],{})
                translate_id = self.env['ir.translation'].search([('name', '=', 'product.template,name'), ('res_id', '=', product_id.id), ('lang', '=',lang)], limit=1)
                
                if import_product_id:
                    if translate_id:
                        if lang == 'en_US' and translate_id:
                            translate_id.value = import_product_id[0].get("value", '')
                        if lang == 'zh_CN' and translate_id:
                            translate_id.value = import_product_id[0].get("value", '')
                        if lang == 'zh_TW' and translate_id:
                            translate_id.value = import_product_id[0].get("value", '')
                        if lang == 'ja_JP' and translate_id:
                            translate_id.value = import_product_id[0].get("value", '')
                        if lang == 'ko_KR' and translate_id:
                            translate_id.value = import_product_id[0].get("value", '') 
                    else:
                        
                        if lang == 'en_US':
                            translated_value = import_product_id[0].get("value", '')
                        if lang == 'zh_CN':
                            translated_value = import_product_id[0].get("value", '')
                        if lang == 'zh_TW':
                            translated_value = import_product_id[0].get("value", '')
                        if lang == 'ja_JP':
                            translated_value = import_product_id[0].get("value", '')
                        if lang == 'ko_KR':
                            translated_value = import_product_id[0].get("value", '') 
                        
                        ir_translation_id = self.env['ir.translation'].create({
                                    'name' : 'product.template,name',
                                    'lang' : lang,
                                    'src' : product_id.name,
                                    'value' : translated_value,
                                    'type' : 'model',
                                    'res_id' : product_id.id,
                                    })
            i+=1      
            self.product_offset = i
            self._cr.commit()
    
        
                
                    
                  
                                   
        