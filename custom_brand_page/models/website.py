# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.http import request


class Website(models.Model):

    _inherit = "website"
    
    def _force_website(self, website_id):
        res = super(Website, self)._force_website(website_id)
        if request:
            request.session['country_filter_id'] = request.session.get('country_filter_id', False)
#     def _force_country_id(self, country_id):
#         self._force_country_website(self.id, country_id)
# 
#     def _force_country_website(self, website_id, country_id):
#         if request:
#             request.session['force_website_id'] = website_id and str(website_id).isdigit() and int(website_id)
#             request.session['country_filter_id'] = country_id.id