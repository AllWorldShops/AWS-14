import requests
from odoo import SUPERUSER_ID, _
from datetime import datetime
from odoo import http
from odoo.http import Controller, route, request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.website.controllers.main import Website
import werkzeug.utils
import werkzeug.wrappers
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from http import cookies
from odoo.addons.website_sale.controllers.main import WebsiteSale



class WebsiteSale(ProductConfiguratorController, Website):

    @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    def pricelist_change(self, pl_id, **post):
        if (pl_id.selectable or pl_id == request.env.user.partner_id.property_product_pricelist) \
                and request.website.is_pricelist_available(pl_id.id):
            request.session['website_sale_current_pl'] = pl_id.id
            request.website.sale_get_order(force_pricelist=pl_id.id)
        return request.redirect(request.httprequest.referrer or '/shop')


