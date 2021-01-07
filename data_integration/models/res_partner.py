# -*- coding: utf-8 -*-

from odoo import api, models, fields,  _
import xmlrpc.client

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    old_id = fields.Integer("Odoo12 ID")

class DataIntegration(models.Model):
    _inherit = "data.integration"
    
    partner_offset = fields.Integer("Partner Offset")
    parent_partner = fields.Boolean("Parent Partner")
    
    def partner_create_cron(self):
        
        data_integ_id = self.env['data.integration'].search([], limit=1)
        if data_integ_id:
            data_integ_id.create_partner()
    
    def create_partner(self):
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()        
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        
#         partner_ids = models.execute_kw(self.db, uid, self.password,'res.partner', 'search_read',[['|',('active','=',False),('active','=',True)]],{'offset': self.partner_offset,})
        partner_ids = models.execute_kw(self.db, uid, self.password,'res.partner', 'search_read',[[('active','=',True)]],{'fields':
        ['parent_id','name','email','lastname','firstname','display_name','supplier','customer',
         'company_type','type','image','active','street','street2','city','zip','phone','mobile','website','lang','vat',
         'ref','tz','comment','credit_limit','employee','function','is_company','color','partner_share','commercial_company_name','company_name','message_bounce','signup_token','signup_type',
         'signup_expiration','debit_limit','last_time_entries_checked','invoice_warn','invoice_warn_msg','sale_warn','sale_warn_msg','website_description','website_short_description','website_meta_title',
         'website_meta_description','website_meta_keywords','picking_warn','picking_warn_msg','purchase_warn','purchase_warn_msg','state_id','country_id']
        
        ,'offset': self.partner_offset,'limit': 1000})
        
        i = self.partner_offset
        if not partner_ids:
            self.partner_offset = self.partner_offset + 1000
            self._cr.commit()  
            
        for partner_id in partner_ids:
            print(partner_id['lastname'], partner_id['firstname'],partner_id['name'],partner_id['display_name'])
            if partner_id['supplier']:
                if self.parent_partner:
                    if partner_id['parent_id']:
                        partner_id = models.execute_kw(self.db, uid, self.password,'res.partner', 'search_read',[[('id','=',partner_id['parent_id'][0])]],{'fields':
            ['parent_id','name','email','lastname','firstname','display_name','supplier','customer',
             'company_type','type','image','active','street','street2','city','zip','phone','mobile','website','lang','vat',
             'ref','tz','comment','credit_limit','employee','function','is_company','color','partner_share','commercial_company_name','company_name','message_bounce','signup_token','signup_type',
             'signup_expiration','debit_limit','last_time_entries_checked','invoice_warn','invoice_warn_msg','sale_warn','sale_warn_msg','website_description','website_short_description','website_meta_title',
             'website_meta_description','website_meta_keywords','picking_warn','picking_warn_msg','purchase_warn','purchase_warn_msg','state_id','country_id']
            ,'limit': 1})
                        
                        if partner_id:
                            partner_id = partner_id[0]
                    
                if not self.env['res.partner'].search([('old_id','=',partner_id['id'])]):
                        supplier = customer = 0
                        if partner_id['supplier']:
                            supplier = 1
                        if partner_id['customer']:
                            customer = 1
                        partner_vals  = {
                                'old_id': partner_id['id'] or False,
                                'company_type': partner_id['company_type'] or False,
                                'type': partner_id['type'] or False,
                                'lastname': partner_id['lastname'] or False,
                                'firstname': partner_id['firstname'] or False,
                                'image_1920': partner_id['image'] or False,
                                'active': True,
                                'street': partner_id['street'] or False,
                                'street2': partner_id['street2'] or False,
                                'city': partner_id['city'] or False,
                                'zip': partner_id['zip'] or False,
                                'phone': partner_id['phone'] or False,
                                'mobile': partner_id['mobile'] or False,
                                'email': partner_id['email'] or False,
                                'website': partner_id['website'] or False,
                                'lang': partner_id['lang'] or False,
                                'vat': partner_id['vat'] or False,
    #                             'skip_payment': partner_id['skip_payment'] or False,
#                                 'display_name': partner_id['display_name'] or False,
#                                 'date': partner_id['date'] or False,
                                'ref': partner_id['ref'] or False,
                                'tz': partner_id['tz'] or False,
                                'comment': partner_id['comment'] or False,
                                'credit_limit': partner_id['credit_limit'] or False,
                                'employee': partner_id['employee'] or False,
                                'function': partner_id['function'] or False,
    #                             'partner_latitude': partner_id['partner_latitude'] or False,
    #                             'partner_longitude': partner_id['partner_longitude'] or False,
                                'is_company': partner_id['is_company'] or False,
                                'color': partner_id['color'] or False,
                                'partner_share': partner_id['partner_share'] or False,
                                'commercial_company_name': partner_id['commercial_company_name'] or False,
                                'company_name': partner_id['company_name'] or False,
                                'message_bounce': partner_id['message_bounce'] or False,
                                'signup_token': partner_id['signup_token'] or False,
                                'signup_type': partner_id['signup_type'] or False,
                                'signup_expiration': partner_id['signup_expiration'] or False,
                                'debit_limit': partner_id['debit_limit'] or False,
                                'last_time_entries_checked': partner_id['last_time_entries_checked'] or False,
                                'invoice_warn': partner_id['invoice_warn'] or False,
                                'invoice_warn_msg': partner_id['invoice_warn_msg'] or False,
                                'sale_warn': partner_id['sale_warn'] or False,
                                'sale_warn_msg': partner_id['sale_warn_msg'] or False,
                                'website_description': partner_id['website_description'] or False,
                                'website_short_description': partner_id['website_short_description'] or False,
                                'website_meta_title': partner_id['website_meta_title'] or False,
                                'website_meta_description': partner_id['website_meta_description'] or False,
                                'website_meta_keywords': partner_id['website_meta_keywords'] or False,
    #                             'calendar_last_notif_ack': partner_id['calendar_last_notif_ack'] or False,
                                'picking_warn': partner_id['picking_warn'] or False,
                                'picking_warn_msg': partner_id['picking_warn_msg'] or False,
                                'purchase_warn': partner_id['purchase_warn'] or False,
                                'purchase_warn_msg': partner_id['purchase_warn_msg'] or False,
                                'supplier_rank' : supplier,
                                'customer_rank' : customer,
                                }
        #                 if partner_id['title']:
        #                     partner_vals['title'] = self.env['res.partner.title'].search([('old_id','=',partner_id['title'][0])]).id
        #                 if partner_id['team_id']:
        #                     partner_vals['team_id'] = self.env['crm.team'].search([('old_id','=',partner_id['team_id'][0])]).id
        #                 if partner_id['commercial_partner_id']:
        #                     partner_vals['commercial_partner_id'] = self.env['res.partner'].search([('old_id','=',partner_id['commercial_partner_id'][0])]).id    
                        if partner_id['state_id']:
        #                     partner_vals['state_id'] = self.env['res.country.state'].search([('old_id','=',partner_id['state_id'][0])]).id
                            partner_vals['state_id'] = self.get_country_by_state(partner_id['state_id'], models, uid)
                        if partner_id['country_id']:
                            partner_vals['country_id'] = self.get_country_by_code(partner_id['country_id'], models, uid)
        #                 if partner_id['user_id']:
        #                     partner_vals['user_id'] = self.env['res.users'].search([('old_id','=',partner_id['user_id'][0])]).id  
            #             if partner_id['property_delivery_carrier_id']:
            #                 partner_vals['property_delivery_carrier_id'] = self.env['delivery.carrier'].search([('old_id','=',partner_id['property_delivery_carrier_id'][0])]).id
        #                 if partner_id['property_payment_term_id']:
        #                     partner_vals['property_payment_term_id'] = self.env['account.payment.term'].search([('old_id','=',partner_id['property_payment_term_id'][0])]).id
        #                 if partner_id['property_supplier_payment_term_id']:
        #                     partner_vals['property_supplier_payment_term_id'] = self.env['account.payment.term'].search([('old_id','=',partner_id['property_supplier_payment_term_id'][0])]).id
            #             if partner_id['property_product_pricelist']:
            #                 partner_vals['property_product_pricelist'] = self.env['product.pricelist'].search([('old_id','=',partner_id['property_product_pricelist'][0])]).id
        #                 if partner_id['property_purchase_currency_id']:
        #                     partner_vals['property_purchase_currency_id'] = self.env['res.currency'].search([('old_id','=',partner_id['property_purchase_currency_id'][0])]).id
        #                 if partner_id['property_account_position_id']:
        #                     partner_vals['property_account_position_id'] = self.env['account.fiscal.position'].search([('old_id','=',partner_id['property_account_position_id'][0])]).id
        #                 if partner_id['property_stock_customer']:
        #                     partner_vals['property_stock_customer'] = self.env['stock.location'].search([('old_id','=',partner_id['property_stock_customer'][0])]).id
        #                 if partner_id['property_stock_supplier']:
        #                     partner_vals['property_stock_supplier'] = self.env['stock.location'].search([('old_id','=',partner_id['property_stock_supplier'][0])]).id
        #                 if partner_id['category_id']:
        #                     partner_vals['category_id'] =  [(6, 0, self.get_many_ids('res.partner.category',partner_id['category_id']))]
                        if partner_id['parent_id']:
                            partner_vals['parent_id'] = self.get_many2one_id(self, models, self.db, uid, self.password, models, partner_id['parent_id'][0])
                        
                        par_id = self.env['res.partner'].search([('old_id','=',partner_id['id'])])
                        if par_id:
                            pass
                        else:
                            c_partner_id = self.env['res.partner'].create(partner_vals)
            i+=1      
            self.partner_offset = i
            self._cr.commit()  
            
#         for pare_id in partner_ids:
#             c_pare_id = self.env['res.partner'].search([('old_id','=',pare_id['id'])])
#             if pare_id['parent_id'] and pare_id['parent_id'][0]:
#                 c_parent_id = self.env['res.partner'].search([('old_id','=',pare_id['parent_id'][0])])
#                 c_pare_id.write({'parent_id': c_parent_id.id})


    def get_country_by_state(self, state_id, models, uid):
        state_id = models.execute_kw(self.db, uid, self.password,'res.country', 'search_read',[[('id','=',state_id[0])]])
        if state_id:
            state_id = self.env['res.country.state'].search([('code','=',state_id[0]['code'])], limit=1)
            if state_id:
                return state_id.id
            
        return False

    
            
