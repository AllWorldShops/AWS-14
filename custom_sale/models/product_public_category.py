# -*- coding: utf-8 -*-

from odoo import models, fields, _, api

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"
    
    country_website_fitler = fields.Boolean("Country on Website?")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        limit=50000
        return super(ProductPublicCategory, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
    
        