from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    country_id=fields.Many2one('res.country',string='Country',related='partner_id.country_id',store=True)
    
    def interCom_currency_check(self, force=False):
        for order in self:
            # get the company from partner then trigger action of intercompany relation
            company_rec = self.env['res.company']._find_company_from_partner(order.partner_id.id)
            if company_rec and company_rec.rule_type in ('purchase', 'sale_purchase') and (not order.auto_generated):
                currency_id = order.with_user(company_rec.intercompany_user_id).with_context(default_company_id=company_rec.id).with_company(company_rec).inter_company_create_sale_order_check(company_rec)
                if currency_id:
                    order.write({"currency_id":currency_id})
                
                
    def inter_company_create_sale_order_check(self, company):
        intercompany_uid = company.intercompany_user_id and company.intercompany_user_id.id or False
        if not intercompany_uid:
            raise UserError(_('Provide at least one user for inter company relation for % ') % company.name)

        for rec in self:
            # check pricelist currency should be same with SO/PO document
            company_partner = rec.company_id.partner_id.with_user(intercompany_uid)
            if rec.currency_id.id != company_partner.property_product_pricelist.currency_id.id:
                return company_partner.property_product_pricelist.currency_id.id
            return False
    
    @api.model
    def create(self, vals):
        purchase_id = super().create(vals)
        purchase_id.interCom_currency_check()
        purchase_id._compute_currency_rate()
        return purchase_id

  