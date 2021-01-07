# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist

import werkzeug


from odoo.http import request

        
class AuthSignupHome(Home):    
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        print("new")
        response = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
        qcontext = self.get_auth_signup_qcontext()
                # Send an account creation confirmation email
        if 'error' not in qcontext:
            user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
            template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
            if user_sudo and template:
                template.sudo().with_context(
                    lang=user_sudo.lang,
                    auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                ).send_mail(user_sudo.id, force_send=True)
             
        return response
    