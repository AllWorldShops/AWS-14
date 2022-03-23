# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError,Warning
# from odoo.addons.mail.models.mail_template import format_tz
#from odoo.addons.mail.models.mail_template import format_datetime
import logging


class ResGroups(models.TransientModel):
	_inherit='portal.wizard.user'	

	def sending_mail(self,force_send=True):
		templ_id=self.env.ref("sales_reward.loyality_card_template").id
		if(templ_id and self.partner_id.email and self.partner_id.customer_type!='exp'):
			self.partner_id.env['mail.template'].browse(templ_id).send_mail(self.partner_id.id, force_send=force_send)

	# @api.constrains('in_portal')
	# def add_new_users(self):	
	# 	if(self.in_portal and self.partner_id):
	# 		self.sending_mail()


