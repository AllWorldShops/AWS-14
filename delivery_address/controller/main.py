import json
import logging
from werkzeug.exceptions import Forbidden, NotFound
import datetime
from datetime import timedelta  
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
# from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):

  
    @http.route(['/shop/product/<model("product.template"):product>','/shop/product','/shop/<model("product.template"):product>'], type='http', auth="public", website=True,sitemap=False)
    def product(self, product, category='', search='', **kw):
        if request.session.uid:
            user_active=True
        else:
            user_active=False
        now = datetime.datetime.now()
        day_num=now.weekday()
        
        pro_obj=request.env['product.template'].sudo().search([("id", "=",product.id)])
        if pro_obj:
            if day_num!=4 and day_num!=5 and day_num!=6 and pro_obj.qty_available>=1:                 
                days=3
                 
            elif day_num==4 and  pro_obj.qty_available>=1: 
                days=3+3
            
            elif day_num==5 and  pro_obj.qty_available>=1: 
                days=2+3
                
            elif day_num==6 and  pro_obj.qty_available>=1: 
                days=1+3
                
            elif pro_obj.qty_available<1: 
                days=3+5
                
        delivery_day=datetime.datetime.now() + timedelta(days)
        d_month= delivery_day.strftime('%B')
        d_date=  delivery_day.strftime('%d')
        
        if delivery_day.weekday() == 0:
            d_day= "Monday"
        if delivery_day.weekday() == 1:
            d_day= "Tuesday"
        if delivery_day.weekday() == 2:
            d_day="Wednesday"
        if delivery_day.weekday() == 3:
            d_day= "Thursday"
        if delivery_day.weekday() == 4:
            d_day= "Friday"
        if delivery_day.weekday() == 5:
            d_day= "Saturday"
        if delivery_day.weekday() == 6:
            d_day= "Sunday"    
       
        if not product.can_access_from_current_website():
            raise NotFound()

        add_qty = int(kw.get('add_qty', 1))
        
      

        product_context = dict(request.env.context, quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)
        
        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        def compute_currency(price):    
            return product.currency_id._convert(price, pricelist.currency_id, product._get_current_company(pricelist=pricelist, website=request.website), fields.Date.today())

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)
            
            
        order = request.website.sale_get_order(force_create=1)   
        shippings = []
        if order.partner_id != request.website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()
            shippings = Partner.search([
                ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                '|', ("type", "in", ["delivery", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
            ], order='id desc')
            if shippings:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))
                    if partner_id in shippings.mapped('id'):
                        order.partner_shipping_id = partner_id
                elif not order.partner_shipping_id:
                    last_order = request.env['sale.order'].sudo().search([("partner_id", "=", order.partner_id.id)], order='id desc', limit=1)
                    order.partner_shipping_id.id = last_order and last_order.id

        
       
        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            # compute_currency deprecated, get from product
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'add_qty': add_qty,
            'optional_product_ids': [p.with_context({'active_id': p.id}) for p in product.optional_product_ids],
            # get_attribute_exclusions deprecated, use product method
#             'get_attribute_exclusions': self._get_attribute_exclusions,
             'order': order,
            'shippings': shippings,
            'days':days ,
            'day':d_day,
            'date':d_date,
            'month':d_month,
            'user_active':user_active,
            'only_services': order and order.only_services or False
        }
        return request.render("website_sale.product", values)
    
    
    @http.route(['/update_delviery_address'], type='http', auth="public", website=True, csrf=False)
    def update_delviery_address(self, **kw):
        order = request.website.sale_get_order()
        if order:
            order.partner_shipping_id = int(kw['ship_id'])
       
        return "True"
    
    @http.route(['/shop/create_address/<int:product>','/shop/create_address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def create_address(self, product=False, **kw):

        current_url = kw.get('url', False) and kw.get('url').replace(",", "/") or request.httprequest.referrer

        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                if order:
                    partner_id = self._checkout_form_save(mode, post, kw)
                    if mode[1] == 'billing':
                        order.partner_id = partner_id
                        order.onchange_partner_id()
                        if not kw.get('use_same'):
                            kw['callback'] = kw.get('callback') or \
                                (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                    elif mode[1] == 'shipping':
                        order.partner_shipping_id = partner_id

                    order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                    if not errors:
                        product = request.env['product.template'].browse(int(product))
                        if current_url:
                            url = current_url
                        else:
                            url = '/shop/product/%s' % slug(product)
                        return request.redirect(kw.get('callback') or url)
                else:                                        
                    user_obj = request.env['res.users'].sudo().search([('id' , '=' , int(request.uid))])
                    partner_obj = request.env['res.partner'].sudo().search([('id' , '=' , user_obj.partner_id.id)])
                    partner_update_obj = partner_obj.sudo().write({
                        'street' : kw['street'],
                        'street2': kw['street2'],
                        'city': kw['city'],
                        'state_id': kw['state_id'],
                        'zip': kw['zip'],
                        'country_id': kw['country_id'],
                        'phone': kw['phone'],
                    })
                    partner_id = partner_obj
                    if current_url:
                        url = current_url
                    return request.redirect(kw.get('callback') or url)

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'product': product,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
#             "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'current_url' : current_url,
        }
        return request.render("delivery_address.create_address", render_values)
    
    def checkout_redirection(self, order):
        # must have a draft sales order with lines at this point, otherwise reset
        # if not order or order.state != 'draft':
        #     request.session['sale_order_id'] = None
        #     request.session['sale_transaction_id'] = None
        #     return request.redirect('/shop')

        # if order and not order.order_line:
        #     return request.redirect('/shop/cart')

        # if transaction pending / done: redirect to confirmation
        tx = request.env.context.get('website_sale_transaction')
        if tx and tx.state != 'draft':
            return request.redirect('/shop/payment/confirmation/%s' % order.id)