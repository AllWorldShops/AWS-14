# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound

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
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.osv import expression
from odoo.addons.emipro_theme_base.controller.main import EmiproThemeBase
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSale
from odoo.addons.emipro_theme_base.controller.main import EmiproThemeBaseExtended
import werkzeug.urls
import werkzeug.utils
from odoo import fields, models, http
from werkzeug import urls

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class Website(models.Model):
    _inherit = "website"
    
    
    def get_shop_products(self, search=False, category=False, attrib_values=False):
        """
        Get the product count based on attribute value and current search domain.
        """
        domain = EmiproThemeBaseExtended._get_search_domain(EmiproThemeBaseExtended(),search, category, attrib_values)
        domain = [dom for dom in domain if not dom[0] == 'product_brand_ept_id.id']
        if category:
            if category.country_website_fitler:
                domain = [dom for dom in domain if not dom[0] == 'public_categ_ids']
                domain = domain + [('website_country_id', '=', category.id)]
                
        Product = request.env['product.template']
        brand_inc_products = search_product = Product.search(domain)
        if attrib_values:
            ids = [attrib[1] for attrib in attrib_values if attrib[0] == 0]
            if ids:
                brand_inc_products = search_product.filtered(lambda r: r.product_brand_ept_id.id in ids)
        return [brand_inc_products,search_product]

    def brand_get_min_max_prices(self, products):
        """
        Get minimum price and maximum price according to Price list as well as discount for Shop page
        :return: min and max price value
        """
        range_list = []
        cust_min_val = request.httprequest.values.get('min_price', 0)
        cust_max_val = request.httprequest.values.get('max_price', 0)

        prices_list = []
        is_web_price = request.website.price_filter_on == 'website_price'
        is_web_price = True
        if products:
            if is_web_price:
                pricelist = self.get_current_pricelist()
                context = dict(self.env.context, quantity=1, pricelist=pricelist.id if pricelist else False)
                products = products.with_context(context).sorted('price')
            else:
                products = products.sorted('lst_price')

        if not products : return False

        if not cust_min_val and not cust_max_val:
            range_list.append(round(products[0].price if is_web_price else products[0].lst_price,2))
            range_list.append(round(products[-1].price if is_web_price else products[-1].lst_price,2))
            range_list.append(round(products[0].price if is_web_price else products[0].lst_price, 2))
            range_list.append(round(products[-1].price if is_web_price else products[-1].lst_price, 2))
        else:
            range_list.append(round(float(cust_min_val),2))
            range_list.append(round(float(cust_max_val),2))
            range_list.append(round(products[0].price if is_web_price else products[0].lst_price, 2))
            range_list.append(round(products[-1].price if is_web_price else products[-1].lst_price, 2))
        return range_list

class EmiproThemeBase(EmiproThemeBase, WebsiteSale):
    
    
    @http.route(['/shop/cart/update_custom'], type='json', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def cart_update_custom(self, product_id, add_qty=1, set_qty=0, product_custom_attribute_values=None, **kw):
       res = super(EmiproThemeBase, self).cart_update(product_id=product_id, add_qty=1, set_qty=0, product_custom_attribute_values=product_custom_attribute_values, **kw)
       return res
   
   
    def _get_products_recently_viewed(self):
        
        if not request.website.website_show_price:
        
            """
            Returns list of recently viewed products according to current user
            """
            max_number_of_product_for_carousel = 12
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor:
                excluded_products = request.website.sale_get_order().mapped('order_line.product_id.id')
                products = request.env['website.track'].sudo().read_group(
                    [('visitor_id', '=', visitor.id), ('product_id', '!=', False), ('product_id.website_published', '=', True), ('product_id', 'not in', excluded_products)],
                    ['product_id', 'visit_datetime:max'], ['product_id'], limit=max_number_of_product_for_carousel, orderby='visit_datetime DESC')
                products_ids = [product['product_id'][0] for product in products]
                if products_ids:
                    viewed_products = request.env['product.product'].with_context(display_default_code=False).browse(products_ids)
    
                    FieldMonetary = request.env['ir.qweb.field.monetary']
                    monetary_options = {
                        'display_currency': request.website.get_current_pricelist().currency_id,
                    }
                    rating = request.website.viewref('website_sale.product_comment').active
                    res = {'products': []}
                    for product in viewed_products:
                        combination_info = product._get_combination_info_variant()
                        res_product = product.read(['id', 'name', 'website_url'])[0]
                        res_product.update(combination_info)
                        res_product['price'] = ''
                        if rating:
                            res_product['rating'] = request.env["ir.ui.view"]._render_template('portal_rating.rating_widget_stars_static', values={
                                'rating_avg': product.rating_avg,
                                'rating_count': product.rating_count,
                            })
                        res['products'].append(res_product)
    
                    return res
            return {}
        else:
          res = super(EmiproThemeBase, self)._get_products_recently_viewed()
          return res
    
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template("website_sale.short_cart_summary", {
            'website_sale_order': order,
        })
        return value
    
    
    @http.route(["/reset_country_filter_details/"], type='http', auth="public", methods=['POST'], website=True,csrf=False)
    def reset_country_filter_details(self, **post):
        request.session['country_filter_id'] = 951
        
        
    @http.route(['/shop/change_category_country/<model("product.public.category"):cate_country_id>'], type='http', auth="public", website=True, sitemap=False)
    def pricelist_change(self, cate_country_id, **post):
        
        request.session['country_filter_id'] = 0
        request.session['country_filter_id'] = cate_country_id.id
        if cate_country_id.website_id:
            cate_country_id.website_id._force()
        
        request.session['country_filter_id'] = cate_country_id.id
        web_url = False
        web_url = request.httprequest.referrer
        if str(request.httprequest.referrer).find("fw=") > -1 and cate_country_id.website_id:
            web_url = str(request.httprequest.referrer).replace("fw=","fw="+str(cate_country_id.website_id.id)+"&") 
        else:
            web_url = request.httprequest.referrer
        
        
        base_url=request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if (not cate_country_id.sudo().category_page):
            web_url = base_url
        else:
            web_url = urls.url_join (base_url ,cate_country_id.sudo().category_page.url)
            
        redirect = werkzeug.utils.redirect(web_url or '/shop', 303)
        return redirect
        return request.redirect(request.httprequest.referrer or '/shop')
    
    
    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        
        
        country_filter_id = 951
        category_domain = []
        
        if 'country_filter_id' in post:
            if post.get('country_filter_id') != '':
                country_filter_id = post.get('country_filter_id')
                request.session['country_filter_id'] = country_filter_id
            else:
                request.session['country_filter_id'] = 0
        
        if request.session.get('country_filter_id', False):
            country_filter_id = request.session['country_filter_id']
        else:
            request.session['country_filter_id'] = 951
            country_filter_id = 951
        
        
        
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        
        # Allworld Shop filters method
        if category:
            
            category = Category.search([('id', '=', int(category))], limit=1)
            
            if category.country_website_fitler:
                if category.name == "Shop the world":
                    category = Category
                else:
                    category_domain = [('website_country_id','=',int(country_filter_id))]
                
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category
            category = Category.search([('id', '=', int(country_filter_id))], limit=1)
            if category.name == "Shop the world":
                category = Category
            else:
                category_domain = [('website_country_id','=',int(country_filter_id))]

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

#         domain = self._get_search_domain(search, category, attrib_values)
        domain = EmiproThemeBaseExtended._get_search_domain(EmiproThemeBaseExtended(), search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)
        
        # All World connect products filters
        awc_domain = []
        
        if request.website.company_id.id == 5:
            awc_domain += [('company_id','=', request.website.company_id.id)]
        
        if category_domain:
            domain = EmiproThemeBaseExtended._get_search_domain(EmiproThemeBaseExtended(), '', '', attrib_values)
            search_product = Product.search(category_domain+domain+awc_domain, order=self._get_search_order(post))
        else:
            search_product = Product.search(category_domain+domain+awc_domain, order=self._get_search_order(post))
            
        website_domain = request.website.website_domain()
        if category:
            website_domain = [('parent_id', 'child_of', category.id)] + website_domain
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
            
        if request.website.company_id.id != 5:
            categs = Category.search(website_domain+[('parent_id', '=', int(country_filter_id))])
        else:
            categs = Category

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
#         products = search_product[offset: offset + ppg]
        products = search_product

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
                
        allworld_shop_id = Category.search([('id', '=', int(country_filter_id))], limit=1)
                
        if allworld_shop_id.name == "Shop the world":
            products = request.env['product.template'].search([('id','in',products.ids if products else [])])
        elif country_filter_id and products:
            products = request.env['product.template'].search([('website_country_id', '=', int(country_filter_id)), ('id','in',products.ids if products else [])])
        
#         elif country_filter_id and not products:
#             products = request.env['product.template'].search([('public_categ_ids', 'in', [int(country_filter_id)])])
        else:
            products = products
        if products:
            if category:
                categs =  categs + products.mapped("public_categ_ids")
                if categs:
#                     categs = Category.search([('id', 'in', categs.ids)])
                    categs = Category.search([('id', '=', int(category))])
            else:
                categs = []
                
            if not categs and country_filter_id == 951:
                categs =  products.mapped("public_categ_ids")
                if categs:
                    categs = Category.search([('id', 'in', categs.ids)])
            
        product_count = len(products or [])
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = request.env['product.template'].search([('id','in',products.ids if products else [])], limit=ppg, offset=pager['offset'] or 0, order=self._get_search_order(post))

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'country_categ_id':int(country_filter_id),
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)  
        
        
    @http.route([
        '/brand/<model("product.brand.ept"):brand>',
        '/brand/page/<int:page>',
        '/brand/<model("product.brand.ept"):brand>/page/<int:page>',
        '''/brand''','''/brand/<int:brand_id>''',
        '''/brand/<model("product.brand.ept"):brand>''',
        '''/brand/<model("product.brand.ept"):brand>/page/<int:page>''',
         '''/brand/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/brand/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>''',
        '''/brand/<model("product.brand.ept"):brand>/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/brand/<model("product.brand.ept"):brand>/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True,sitemap=WebsiteSale.sitemap_shop)
    def Brand(self, brand_id=False, brand=False, page=0, category=0, search='', ppg=False, **post):
        
        keep = QueryURL('/brand')
        
        
        country_filter_id = 951
        
        if 'country_filter_id' in post:
            if post.get('country_filter_id') != '':
                country_filter_id = post.get('country_filter_id')
                request.session['country_filter_id'] = country_filter_id
            else:
                request.session['country_filter_id'] = 951
        
        if request.session.get('country_filter_id', False):
            country_filter_id = request.session['country_filter_id']
        
        
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
            
        if category:
            category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
            if category.country_website_fitler:
                category = 0
        
        brand_ids = request.env['product.brand.ept'].sudo().search([('website_published','=',True),('website_id','=',request.website.id if request.website else False)])

        values = {
#             'pager': pager,
#             'bins': TableCompute().brandProcess(brand_ids, ppg),
            'rows': PPR,
            'keep': keep,
            'brand_ids': brand_ids,
        }
        if brand_id or brand or category:
            
            brand_id = request.env['product.brand.ept'].sudo().search([('id','=',int(brand_id))]) or brand
            
            attributes_products = []
            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}
            
#             attrib_domain = self._get_search_domain(search, '', attrib_values)
            
            attrib_domain = EmiproThemeBaseExtended._get_search_domain(EmiproThemeBaseExtended(), search, category, attrib_values)
            
            keep = QueryURL('/brand/%s' % brand_id.id, category=category and int(category), search=search, attrib=attrib_list)
            
            product_count = len(brand_id.product_ids or [])
            url = "/brand/%s" % slug(brand_id)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = brand_id.product_ids.search([('id','in',brand_id.product_ids.ids if brand_id.product_ids else [])])
            attributes_products = products
            if category:
                products = brand_id.product_ids.search([('public_categ_ids','in',(category.id)), ('id','in',brand_id.product_ids.ids if brand_id.product_ids else [])], order=self._get_search_order(post))
                product_count = len(products.ids if products else [])
                url = "/brand/%s/category/%s" % (slug(brand_id),slug(category))
                pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
                products = brand_id.product_ids.search([('public_categ_ids','in',(category.id)), ('id','in',brand_id.product_ids.ids if brand_id.product_ids else [])])
#                 product_count = len(products.ids if products else [])
#                 pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
                
            if brand_id.product_ids:
                categories = brand_id.product_ids.mapped('public_categ_ids')
            else:
                categs = []
            Category = request.env['product.public.category']
            search_categories = False
            categories = brand_id.product_ids.mapped('public_categ_ids')
            search_categories = Category.search([('id', 'parent_of', categories.ids)])
            categs = search_categories.filtered(lambda c: not c.parent_id)
    
            parent_category_ids = []
            if category:
                parent_category_ids = [category.id]
                current_category = category
                while current_category.parent_id:
                    parent_category_ids.append(current_category.parent_id.id)
                    current_category = current_category.parent_id
            
            allworld_shop_id = Category.search([('id', '=', int(country_filter_id))], limit=1)
                
            if allworld_shop_id.name == "Shop the world":
                products = request.env['product.template'].search([('id','in',products.ids if products else [])])
            elif country_filter_id and products:
                products = request.env['product.template'].search([('website_country_id', '=', int(country_filter_id)), ('id','in',products.ids if products else [])])
                
#             elif country_filter_id and not products:
#                 products = request.env['product.template'].search([('public_categ_ids', 'in', [int(country_filter_id)])], limit=ppg, offset=pager['offset'] or 0, order=self._get_search_order(post))
            else:
                products = products
                
                
            ProductAttribute = request.env['product.attribute']
            if attributes_products:
                # get all products without limit
                attributes = ProductAttribute.search([('product_tmpl_ids', 'in', attributes_products.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)
            
            product_count = len(products or [])
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = request.env['product.template'].search(attrib_domain+[('id','in',products.ids if products else [])], limit=ppg, offset=pager['offset'] or 0, order=self._get_search_order(post))
            
                
            if attrib_list:
                post['attrib'] = attrib_list    
            
            
            if not category:
                category = request.env['product.public.category'].search([('id', '=', int(country_filter_id))], limit=1)
            
            values.update({
                'pager': pager,
                'product_count': product_count,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'attributes': attributes,
                'attributes_products':products,
                'brand_id': brand_id,
                'category': category,
                'categories': categs,
                'parent_category_ids': parent_category_ids,
                'search_categories_ids': search_categories and search_categories.ids or [],
                'bins': TableCompute().process(products, ppg, PPR),
                'rows': PPR,
                'ppg': ppg,
                'ppr': PPR,
                'country_categ_id':int(country_filter_id),
                })
            return request.render("custom_brand_page.brand_info", values)
        else:
            return request.render("custom_brand_page.brands", values)
        
    @http.route(['/brand/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def brand_product(self, product, category='', brand_id=False, search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()

        add_qty = int(kwargs.get('add_qty', 1))

        product_context = dict(request.env.context, quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/brand/%s' % product.product_brand_ept_id.id, category=category and int(category), search=search, attrib=attrib_list)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        def compute_currency(price):
            return product.currency_id._convert(price, pricelist.currency_id, product._get_current_company(pricelist=pricelist, website=request.website), fields.Date.today())

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        values = {
            'search': search,
            'brand_id': product.product_brand_ept_id,
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
            'get_attribute_exclusions': product._get_attribute_exclusions,
        }
        return request.render("website_sale.product", values)

from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery

class websitesaledelivery(EmiproThemeBase, WebsiteSaleDelivery):
    
    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        return super(websitesaledelivery, self).payment(**post)
    
