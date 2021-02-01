# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import date, timedelta

class CustomInvoicePayments(models.Model):
    _inherit = "account.payment"
            

    def post(self):       
        settings=self.env['res.partner'].get_setting_values()
        if self.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
            point_duration = settings['ind_point_duration']
        elif self.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
            point_duration = settings['pro_point_duration']
            
        elif self.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
            point_duration = settings['vip_point_duration']
            
        else:
            amount_per_point = 0
            point_duration = 0  

        if settings['is_website_reward'] and self.partner_id.name:
            if self.amount > 0 and self.invoice_ids.point_to_use:
                valid_point_redeem = 0
                valid_point_redeem_cat = settings['valid_product_category']
                for inv_line in self.invoice_ids.invoice_line_ids:
                    if inv_line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
                        valid_point_redeem += inv_line.price_subtotal              
                
                if(settings['point_credit_cond']=='confirm'):
                    if(int(settings['earn_point_mini_amount']) < valid_point_redeem):
                        if(settings['amount_value_point']):
                            self.invoice_ids.partner_id.total_points += (round(valid_point_redeem)/settings['amount_value_point'])*settings['points_for_amount']

                self.invoice_ids.partner_id.total_amount = self.invoice_ids.partner_id.total_points * amount_per_point
                self.invoice_ids.amount_of_web_points = self.invoice_ids.partner_id.total_amount
                if (round(valid_point_redeem) > 0):
                    self.partner_id.validity_redeem_points = date.today() + timedelta(days=point_duration)
                    print(self.partner_id.validity_redeem_points)
            else:
                self.partner_id.total_points += 0 
            res = super(CustomInvoicePayments, self).post()
            if self.invoice_ids.point_to_use and settings['point_credit_cond']=='confirm':
                self.invoice_ids.partner_id.total_points -= self.invoice_ids.point_to_use
                self.invoice_ids.partner_id.total_amount -= (self.invoice_ids.point_to_use*amount_per_point)
                self.partner_id.remaining_points = self.invoice_ids.partner_id.total_points-self.invoice_ids.point_to_use
        if settings['is_send_mail'] and self.partner_id.is_website_user:
            template = self.env.ref('sales_reward.custom_email_view')
            self.env['mail.template'].browse(template.id).send_mail(self.partner_id.id)
            return res
   

           

