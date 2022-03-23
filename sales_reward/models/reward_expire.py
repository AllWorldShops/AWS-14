# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta


class RewardExpire(models.Model):
    _name = "reward.expire"
    _order = "reward_date desc"
    
    reward_option = fields.Selection([('pos','POS'),('website','Website'),('delivery','Delivery')], string="Sale")
    reward_date = fields.Datetime(string="Reward Date", default=lambda self: fields.Datetime.now())
    reward_expire_date = fields.Datetime(string="Reward Expire Date")
    reward_point = fields.Float(string="Reward Point")
    used_reward_point = fields.Integer(string="Used Reward Point")
    remaining_reward_point = fields.Integer(string="Remaining Reward Point")
    remaining_reward_point1 = fields.Integer(string="Remaining Reward Point", compute="_get_remaining_point")
    amount_per_point =  fields.Float(string="Amount per Point")
    sale_id = fields.Many2one("sale.order", string="Sale")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    pos_id = fields.Many2one("pos.order", string="POS")
    partner_id = fields.Many2one("res.partner", string="Customer")
    reference = fields.Char(string="Reference")
    
    
    def _get_remaining_point(self):
        
        
        for rec in self:
            if rec.reward_option:
                if fields.Datetime.now() >= rec.reward_expire_date:
                    print(rec.remaining_reward_point, "Remaining")
                    if rec.remaining_reward_point:
                        total_web_points = rec.partner_id.total_points - rec.remaining_reward_point
                        print(rec.remaining_reward_point)
                        amount_per_point = rec.remaining_reward_point * rec.amount_per_point
                        self._cr.execute('UPDATE res_partner '\
                           'SET total_points=%s, total_amount=%s '\
                           'WHERE id IN %s', (0 if total_web_points <= 0 else total_web_points, 0 if (rec.partner_id.total_points-amount_per_point) <= 0 else (rec.partner_id.total_amount-amount_per_point), tuple(rec.partner_id.ids),))
                        if total_web_points <= 0:
                            self._cr.execute('UPDATE reward_expire '\
                           'SET remaining_reward_point=%s '\
                           'WHERE id IN %s', (0, tuple(rec.ids),))
                            rec.remaining_reward_point1 = 0
                        elif total_web_points > 0:
                            rec.remaining_reward_point1 = 0
                    else:
                        rec.remaining_reward_point1 = 0
    #                     self.invalidate_cache()
                else:
                    rec.remaining_reward_point1 = rec.reward_point - rec.used_reward_point
            else:
                rec.remaining_reward_point1 = 0
        
#         for rec in self:
#             if rec.reward_option == 'website':
#                 if fields.Datetime.now() >= rec.reward_expire_date:
#                     print(rec.remaining_reward_point, "Remaining")
#                     if rec.remaining_reward_point:
#                         total_web_points = rec.partner_id.total_web_points - rec.remaining_reward_point
#                         print(rec.remaining_reward_point)
#                         amount_per_point = rec.remaining_reward_point * rec.amount_per_point
#                         self._cr.execute('UPDATE res_partner '\
#                            'SET total_web_points=%s, amount_of_web_points=%s '\
#                            'WHERE id IN %s', (0 if total_web_points <= 0 else total_web_points, 0 if (rec.partner_id.amount_of_web_points-amount_per_point) <= 0 else (rec.partner_id.amount_of_web_points-amount_per_point), tuple(rec.partner_id.ids),))
#                         if total_web_points <= 0:
#                             self._cr.execute('UPDATE reward_expire '\
#                            'SET remaining_reward_point=%s '\
#                            'WHERE id IN %s', (0, tuple(rec.ids),))
#                             rec.remaining_reward_point1 = 0
#     #                     self.invalidate_cache()
#                 else:
#                     rec.remaining_reward_point1 = rec.reward_point - rec.used_reward_point
#     #                 self._cr.execute('UPDATE reward_expire '\
#     #                        'SET remaining_reward_point=%s '\
#     #                        'WHERE id IN %s', ((rec.reward_point - rec.used_reward_point), tuple(rec.ids),))
#     
#             elif rec.reward_option == 'pos':
#                 if fields.Datetime.now() >= rec.reward_expire_date:
#                     print(rec.remaining_reward_point, "Remaining")
#                     if rec.remaining_reward_point:
#                         total_pos_points = rec.partner_id.total_pos_points - rec.remaining_reward_point
#                         print(rec.remaining_reward_point)
#                         amount_per_point = rec.remaining_reward_point * rec.amount_per_point
#                         self._cr.execute('UPDATE res_partner '\
#                            'SET total_pos_points=%s, amount_of_pos_points=%s '\
#                            'WHERE id IN %s', (0 if total_pos_points <= 0 else total_pos_points, 0 if (rec.partner_id.amount_of_web_points-amount_per_point) <= 0 else (rec.partner_id.amount_of_web_points-amount_per_point), tuple(rec.partner_id.ids),))
#                         if total_pos_points <= 0:
#                             self._cr.execute('UPDATE reward_expire '\
#                            'SET remaining_reward_point=%s '\
#                            'WHERE id IN %s', (0, tuple(rec.ids),))
#                             rec.remaining_reward_point1 = 0
#     #                     self.invalidate_cache()
#                 else:
#                     rec.remaining_reward_point1 = rec.reward_point - rec.used_reward_point
                    
#             else:
#                 rec.remaining_reward_point1 = 0
    
        
        
  