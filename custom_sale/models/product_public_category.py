# -*- coding: utf-8 -*-

from odoo import models, fields, _

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"
    
    country_website_fitler = fields.Boolean("Country on Website?")
    
        