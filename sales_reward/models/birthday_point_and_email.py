# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class email_trigger(models.Model):

    _inherit = 'res.partner'

    def create_send_mail(self, customer):
       
        email_template_obj = self.env['mail.template']
        template_ids = self.env['ir.model.data'].get_object_reference(
            'sales_reward', 'email_template_customer_birthday_form')[1]
        email = customer['email']
        name = customer['name']

        email_template = email_template_obj.search([('id', '=', template_ids)])
        if email_template:
            values = email_template.generate_email(customer['id'])  
            values['email_to'] = email
            values['record_name'] = name
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                msg_id.send(customer['id'])
        return True

    def email_trigger_action(self): 
        settings=self.env['res.partner'].get_setting_values()

        today = datetime.datetime.today().strftime('%m-%d')
        customer_data = self.env['res.partner'].search([('id', '>', "0")])
        for val in customer_data:
            if val.birthdate: 
                birth_date = val.birthdate[5:]
                if birth_date == today:
                    if settings['is_birthday_points'] :
                        birthdate_points=settings['birthday_points']
                        if settings['is_website_reward'] and val.is_website_user:
                            val.total_web_points+=birthdate_points
                            val.amount_of_web_points= val.total_web_points*(settings['website_amount_per_point'])
                        elif settings['is_pos_reward'] and val.is_pos_user:
                                val.total_pos_points+=birthdate_points
                                val.amount_of_pos_points=val.total_pos_points*(settings['pos_amount_per_point'])
                        self.create_send_mail(val)
        return True