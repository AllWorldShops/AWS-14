# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def get_partner_type_product(self):
        reward_product=0
        if(self.partner_id.customer_type=='ind'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_ind')])
        elif(self.partner_id.customer_type=='vip'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_vip')])
        elif(self.partner_id.customer_type=='pro'):
            reward_product = self.env['product.product'].search([('default_code','=','reward_pro')])
        return reward_product

    def action_create_payments(self):

        super(AccountPaymentRegister,self).action_create_payments()

        settings = self.env['res.partner'].get_setting_values()
        if self.partner_id.customer_type == 'ind':
            amount_per_point = settings['ind_amount_per_point']
            point_duration = settings['ind_point_duration']
            if not amount_per_point:
                amount_per_point = 0
                point_duration = 0
        elif self.partner_id.customer_type == 'pro':
            amount_per_point = settings['pro_amount_per_point']
            point_duration = settings['pro_point_duration']

        elif self.partner_id.customer_type == 'vip':
            amount_per_point = settings['vip_amount_per_point']
            point_duration = settings['vip_point_duration']

        else:
            amount_per_point = 0
            point_duration = 0

        if not amount_per_point:
            amount_per_point = 0
            point_duration = 0

        if settings['is_website_reward'] and self.partner_id.name and self.line_ids.move_id.move_type == 'out_invoice':

            if self.amount > 0 and self.line_ids.move_id.point_to_use:
                valid_point_redeem = self.line_ids.move_id.amount_total
                valid_point_redeem_cat = settings['valid_product_category']

                # for inv_line in self.move_id.invoice_line_ids:
#                 for inv_line in self.line_ids.move_id.invoice_line_ids:
#                     if inv_line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
#                         valid_point_redeem += inv_line.price_subtotal

#                 reward_product_sum = 0
#                 reward_product = self.get_partner_type_product()
#                 for inv_line in self.line_ids.move_id.invoice_line_ids:
#                     if inv_line.product_id == reward_product:
#                         reward_product_sum += inv_line.price_subtotal

                if amount_per_point != 0:
                    earn_points = ((valid_point_redeem) / amount_per_point)
                else:
                    earn_points = 0

                if (settings['point_credit_cond'] == 'confirm'):
                    if (int(settings['earn_point_mini_amount']) < valid_point_redeem):
                        # if (settings['amount_value_point']):
                        #     self.line_ids.move_id.partner_id.total_points += (round(valid_point_redeem) / settings[
                        #         'amount_value_point']) * settings['points_for_amount']
                        self.line_ids.move_id.partner_id.total_points += round(earn_points)

                self.line_ids.move_id.partner_id.total_amount = self.line_ids.move_id.partner_id.total_points * amount_per_point

                self.line_ids.move_id.amount_of_web_points = self.line_ids.move_id.partner_id.total_amount

                if (round(valid_point_redeem) > 0):
                    self.line_ids.move_id.partner_id.validity_redeem_points = date.today() + timedelta(days=point_duration)

            elif self.amount > 0 and self.line_ids.move_id.point_to_use == 0:
                valid_point_redeem = self.line_ids.move_id.amount_total
#                 valid_point_redeem_cat = settings['valid_product_category']
#                 for inv_line in self.line_ids.move_id.invoice_line_ids:
#                     if inv_line.product_id.product_tmpl_id.categ_id.id in valid_point_redeem_cat:
#                         valid_point_redeem += inv_line.price_subtotal

                if amount_per_point != 0:
                    earn_points = ((valid_point_redeem) / amount_per_point)
                else:
                    earn_points = 0

                if (settings['point_credit_cond'] == 'confirm'):
                    if (int(settings['earn_point_mini_amount']) < valid_point_redeem):
                        self.line_ids.move_id.partner_id.total_points += round(earn_points)

            else:
                self.line_ids.move_id.partner_id.total_points += 0
            # res = super(CustomInvoicePayments, self).action_post()

            if self.line_ids.move_id.point_to_use and settings['point_credit_cond'] == 'confirm' and self.line_ids.move_id.move_type == 'out_invoice':
                self.line_ids.move_id.partner_id.total_points -= self.line_ids.move_id.point_to_use

                self.line_ids.move_id.partner_id.total_amount -= (self.line_ids.move_id.point_to_use * amount_per_point)

                self.line_ids.move_id.partner_id.remaining_points = self.line_ids.move_id.partner_id.total_points - self.line_ids.move_id.point_to_use
                
                
#                  Added by jana
                print("point_to use")
                point_to_use = self.line_ids.move_id.point_to_use
                expire_ids = self.env['reward.expire'].search([('partner_id','=',self.line_ids.move_id.partner_id.id),('remaining_reward_point','>',0)], order = "reward_date asc")
                used_point = 0
                for expire_id in expire_ids:
                    print(expire_id.reward_date)
                    remaining_reward_point = expire_id.remaining_reward_point
                    used_point = point_to_use
                    point_to_use = point_to_use - expire_id.remaining_reward_point
                    if point_to_use < 0:
                        expire_id.remaining_reward_point = abs(point_to_use)
                        expire_id.used_reward_point = expire_id.used_reward_point+abs(used_point)
                        break
                    elif point_to_use > 0:
                        expire_id.remaining_reward_point = 0
                        expire_id.used_reward_point = expire_id.used_reward_point+remaining_reward_point
                    elif point_to_use == 0:
                        expire_id.remaining_reward_point = 0
                        expire_id.used_reward_point = expire_id.used_reward_point+remaining_reward_point
                        break
                
                
#                     Added by jana
                
                
            if self.line_ids.move_id.move_type == 'out_invoice':
            
                sale_id = False
                print(self.line_ids.move_id.invoice_line_ids[0].sale_line_ids.mapped('order_id'))
                for line_id in self.line_ids.move_id.invoice_line_ids:
                    sale_id = line_id.sale_line_ids.mapped('order_id')
                    if sale_id:
                        sale_id = sale_id.id
                        break
                    
                expire_vals={
                        'reward_option':'website',
                        'reward_date':fields.Datetime.now(),
                        'reward_expire_date':fields.Datetime.now() + relativedelta(years=1),
                        'reward_point':int(round(earn_points)),
                        'remaining_reward_point':int(round(earn_points)),
                        'amount_per_point':amount_per_point,
                        'sale_id': sale_id,
                        'invoice_id':self.line_ids.move_id.id,
                        'partner_id':self.line_ids.move_id.partner_id.id,
                        }
                expire_id = self.env['reward.expire'].create(expire_vals)
                print(expire_id)
                    
                    
                
                
                

        if settings['is_send_mail'] and self.partner_id.is_website_user:
            template = self.env.ref('sales_reward.custom_email_view')
            self.env['mail.template'].browse(template.id).send_mail(self.partner_id.id)
            # return res



