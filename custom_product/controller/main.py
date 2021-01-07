from odoo import http, tools, _
from odoo.http import request
import logging
import json
_logger = logging.getLogger(__name__)


class WebsiteCartchange(http.Controller):
    @http.route(['/website-cart-change'], type='http', auth="public", website=True, csrf=False)
    def website_cart_change(self,**post):
        weight = lbs = gram = 0
        order_line_id = False
        print(post)
        if request.session['sale_order_id']:
            weight = lbs = gram = 0
            sale_order_id = request.env['sale.order'].sudo().search([('id','=',request.session['sale_order_id'])])
            _logger.info(sale_order_id)
            weight = sale_order_id.get_sale_weight()
#             {"line_id'": '12', 'product_id': '107', 'set_qty': '11'}
            if post.get("line_id", False):
                order_line_id = request.env['sale.order.line'].sudo().search([('id','=',post.get("line_id"))], limit=1)
                total_weight = 0
                if order_line_id:
                    if float(order_line_id.product_uom_qty) != float(post.get("set_qty", 0.0)):
                        total_weight = 0
                        for line in sale_order_id.order_line:
                            if line.id == order_line_id.id:
                                total_weight = (line.product_id.weight * float(post.get("set_qty", 0))) + total_weight
                            else:
                                total_weight = (line.product_id.weight * line.product_uom_qty) + total_weight
                    weight = total_weight
                    
            lbs = (weight * 2.2)
            gram = weight * 1000
        return json.dumps({"weight":round(weight, 4),"gram":round(gram, 4), "lbs":round(lbs,4)})
