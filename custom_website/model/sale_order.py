from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _
from datetime import datetime
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

WEBSITE_STATE = [
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('partially_invoiced', 'Partially Invoiced'),
        ('invoiced', 'Fully Invoiced'),
        ('payment', 'Payment Received'),
        ('partially_shipped', 'Partially shipped'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Order Cancelled'),
        ('partially_refund', 'Partially Refund'),
        ('refunded', 'Refunded'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
    ]


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    website_state = fields.Selection(WEBSITE_STATE, compute='getWebsiteState', string="State")
    
    @api.depends('invoice_ids', 'picking_ids', 'state')
    def getWebsiteState(self):
        for sale_id in self:
            refund = sale_id.invoice_ids.filtered(lambda rec: not rec.state in ('cancel', 'paid') and rec.type == 'out_refund')
            paid_refund = sale_id.invoice_ids.filtered(lambda rec: rec.state in ('paid') and rec.type == 'out_refund') 
            
            inv_ids = [inv for inv in sale_id.invoice_ids if not inv.state == 'cancel']
            paid_inv_ids = [inv for inv in sale_id.invoice_ids if not inv.state in ('cancel', 'paid')]
            
            del_picking_ids = sale_id.picking_ids.filtered(lambda rec: not rec.state in ('cancel', 'done'))
            done_picking_ids = sale_id.picking_ids.filtered(lambda rec: rec.state in ('done')) 
            
            return_picking_ids = sale_id.picking_ids.filtered(lambda rec: rec.state in ('done') and rec.picking_type_code == 'incoming') 
            
            deliver_date_id = sale_id.picking_ids.search([('id', 'in', sale_id.picking_ids.ids), ('state', '=', 'done'), ('picking_type_code', '=', 'outgoing')], order='date_done asc', limit=1)
            days = 0
            if deliver_date_id:
                between = datetime.now() - deliver_date_id.date_done
                days = between.days
                print("deliver date:", deliver_date_id.date_done, days)
                
            if days > 15:
                if not sale_id.website_state == 'completed':
                    sale_id.website_state = 'completed'
            elif sale_id.state in ('cancel'):
                if not sale_id.website_state == 'cancelled':
                    sale_id.website_state = 'cancelled'
            elif sale_id.state in ('draft', 'sent'):
                if not sale_id.website_state == 'processing':
                    sale_id.website_state = 'processing'
            elif refund and paid_refund:
                if not sale_id.website_state == 'partially_refund':
                    sale_id.website_state = 'partially_refund'
            elif refund:
                if not sale_id.website_state == 'partially_refund':
                    sale_id.website_state = 'partially_refund'
            elif paid_refund:
                if not sale_id.website_state == 'refunded':
                    sale_id.website_state = 'refunded'
            elif sale_id.invoice_status == 'invoiced' and not paid_inv_ids:
                if not sale_id.website_state == 'payment':
                    sale_id.website_state = 'payment'
            elif sale_id.invoice_status == 'invoiced' and not paid_inv_ids:
                if not sale_id.website_state == 'payment':
                    sale_id.website_state = 'payment'
            elif sale_id.invoice_status == 'invoiced':
                if not sale_id.website_state == 'invoiced':
                    sale_id.website_state = 'invoiced'
            elif not sale_id.invoice_status == 'invoiced' and inv_ids:
                if not sale_id.website_state == 'partially_invoiced':
                    sale_id.website_state = 'partially_invoiced'
            elif return_picking_ids:
                if not sale_id.website_state == 'returned':
                    sale_id.website_state = 'returned'
            elif del_picking_ids and done_picking_ids:
                if not sale_id.website_state == 'partially_shipped':
                    sale_id.website_state = 'partially_shipped'
            elif not del_picking_ids and done_picking_ids:
                if not sale_id.website_state == 'shipped':
                    sale_id.website_state = 'shipped'
            elif sale_id.state == 'sale':
                if not sale_id.website_state == 'confirmed':
                    sale_id.website_state = 'confirmed'
            elif sale_id.state == 'done':
                if not sale_id.website_state == 'completed':
                    sale_id.website_state = 'completed'
            else:
                _logger.info(str(sale_id.state)+str(sale_id.website_state))
                
    
    @api.model
    def create(self, vals):
        res_id = super(SaleOrder, self).create(vals)
        res_id.getWebsiteState()
        return res_id
    
#     @api.multi
    def write(self, vals):
        for record in self:
            record.getWebsiteState()
        res_id = super(SaleOrder, self).write(vals)
        return res_id

# // Mail to send when payment is done    
#     @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('custom_website', 'email_template_edi_sale_custom')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
#             'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class Picking(models.Model):
    _inherit = "stock.picking"

#     @api.multi
    def action_send_confirmation_email(self):
        self.ensure_one()
        delivery_template_id = self.env.ref('custom_website.email_template_shipping_stock_custom').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,
            default_model='stock.picking',
            default_use_template=bool(delivery_template_id),
            default_template_id=delivery_template_id,
#             custom_layout='mail.mail_notification_light'
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    acquirer_order_confirmation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],
        string='Automatic Confirmation on Online payment', default='no', help="This confirms the sale order if given yes while doing the payment from online acquirers like paypal")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        obj = (ICPSudo.get_param('custom_website.acquirer_order_confirmation'))
        res.update(
            acquirer_order_confirmation=obj
        )
        return res

#     @api.multi
    def set_values(self):
        for record in self:
            super(ResConfigSettings, record).set_values()
            ICPSudo = self.env['ir.config_parameter'].sudo()
            ICPSudo.set_param("custom_website.acquirer_order_confirmation", record.acquirer_order_confirmation)


# // Payment Paypal order confirmation
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

#     @api.multi
    def _reconcile_after_transaction_done(self):
        # Validate invoices automatically upon the transaction is posted.
        invoices = self.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
        invoices._post()

        # Create & Post the payments.
        payments = defaultdict(lambda: self.env['account.payment'])
        for trans in self:
            if trans.payment_id:
                payments[trans.acquirer_id.company_id.id] += trans.payment_id
                continue

            payment_vals = trans._prepare_account_payment_vals()
            payment = self.env['account.payment'].create(payment_vals)
            payments[trans.acquirer_id.company_id.id] += payment

            # Track the payment to make a one2one.
            trans.payment_id = payment

        for company in payments:
            payments[company].with_context(force_company=company, company_id=company).post()
        # Override of '_set_transaction_done' in the 'payment' module
        # to confirm the quotations automatically and to generate the invoices if needed.
        ir_values = self.env['ir.config_parameter'].sudo().get_param('custom_website.acquirer_order_confirmation')
        
        if ir_values == 'yes':
            sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
            for so in sales_orders:
                # For loop because some override of action_confirm are ensure_one.
                so.with_context(send_email=True).action_confirm()
            # invoice the sale orders if needed
            self._invoice_sale_orders()

        if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            default_template = self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
            if default_template:
                ctx_company = {'company_id': self.acquirer_id.company_id.id,
                               'force_company': self.acquirer_id.company_id.id,
                               'mark_invoice_as_sent': True,
                               }
                for trans in self.filtered(lambda t: t.sale_order_ids):
                    trans = trans.with_context(ctx_company)
                    for invoice in trans.invoice_ids:
                        invoice.message_post_with_template(int(default_template), notif_layout="mail.mail_notification_paynow")

