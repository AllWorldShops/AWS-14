# -*- coding: utf-8 -*-

from odoo import models, fields, _, api

from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = "sale.order"




    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False
        if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
            if self.env.company.id == 5:
                template_id = self.env.ref('custom_sale.mail_template_custom_sale_confirmation', raise_if_not_found=False).id
            else:
                print("\n\n\n\n\nqqqq--->",template_id)
                template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
                template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)
        print("\n\n\n\n\n--->",template_id)
        return template_id