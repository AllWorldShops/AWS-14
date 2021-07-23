from odoo import fields, http, tools, _
from odoo.addons.sale.controllers.variant import VariantController
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleReward(VariantController):

    @http.route(['/shop/cart/reward'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def reward(self,point_to_use,**post):
        order = request.website.sale_get_order()
        user=request.env.user.partner_id
        if point_to_use=='':
            point_to_use='0'
        point_cal=order.change_selected_redeemable_amount(point_to_use, user)
        if point_cal!= True:
            if 'warning' in point_cal:
                redirect = post.get('r', '/shop/cart')
                if 'error' in point_cal and point_cal['error']=='1':
                    return request.redirect("%s?reward_error_one=1" % redirect)
                if 'error' in point_cal and point_cal['error']=='2':
                    return request.redirect("%s?reward_error_two=2" % redirect)
                if 'error' in point_cal and point_cal['error']=='3':
                    return request.redirect("%s?reward_error_three=3" % redirect)
                if 'error' in point_cal and point_cal['error']=='4':
                    return request.redirect("%s?reward_error_four=4" % redirect)
                if 'error' in point_cal and point_cal['error']=='5':
                    return request.redirect("%s?reward_error_five=5" % redirect)
                if 'error' in point_cal and point_cal['error']=='6':
                    return request.redirect("%s?reward_error_six=6" % redirect)
                if 'error' in point_cal and point_cal['error']=='7':
                    return request.redirect("%s?reward_error_seven=7" % redirect)
                if 'error' in point_cal and point_cal['error']=='8':
                    return request.redirect("%s?reward_error_eight=8" % redirect)        
        else:
            request.params['hide_reward']=True
        return request.redirect('/shop/cart')
    @http.route(['/product/confirmation'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def confirmation(self,product_id):
        if(product_id.get('product_id')):
            product_id = int(product_id.get('product_id'))
            data = request.env['product.product'].sudo().search([('id','=',product_id),('default_code','in',['reward_ind','reward_pro','reward_vip'])])
            if(data):
                return True
        return False

class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):

        order = request.website.sale_get_order()
        point_cal = order._amount_all()
        redirect = post.get('r', '/shop/cart')
        # if request.website.sale_get_order().amount_total <= 0:
        #     return request.redirect("%s?reward_error_one=11" % redirect)
        if request.website.sale_get_order().amount_total <= 0:
            if point_cal != True:
                if 'warning' in point_cal:
                    if 'error' in point_cal and point_cal['error'] == '11':
                        # return "Invalid Order!"
                        return request.redirect("%s?reward_error_one=11" % redirect)
        else:
            return super(CustomWebsiteSale,self).checkout()