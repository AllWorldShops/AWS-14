# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import base64
from time import gmtime
import datetime
from datetime import date
from ast import literal_eval


# // Wizard to import the csv file for users
class BaseUsersImport(models.TransientModel):
    _name = "base.users.import"
    _description = "Users Import"

    file_import = fields.Binary('File', required=True, attachment=True)
    filename = fields.Char('File Name', required=True)

# // Button action to import users
#     @api.multi
    def import_users(self):
        if self.file_import:
            # // Extraction of data from the csv file
            file_value = self.file_import.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import a 'csv' file")
            input_file = base64.b64decode(file_value)
            lst = []
            for loop in input_file.decode("utf-8").split("\n"):
                l = loop.replace(u'\ufeff', '')
                vals = l.replace('\r', '')
                lst.append([vals])
            
            # // Deletes the heading of the csv file
            lst.pop(0)
            
            # // Creates the users/partners
            language = False
            city = False
            iso_code = False
            zip_id = False
            partner_aid = False
            partner_uid = False
            phone = False
            street = False
            street1 = False
            country_id = False
            dob = False
            title = False
            country_name = False
            for res in lst:
                if res[0]:
                    user = res[0].split(',')
                    if user[6] != '""':
                        if user[6] == "en":
                            iso_code = "en"    
                        if user[6] == "de":
                            iso_code = "de"    
                        if user[6] == "es":
                            iso_code = "es"    
                        if user[6] == "fr":
                            iso_code = "fr"    
                        if user[6] == "ja":
                            iso_code = "ja"    
                        if user[6] == "ko":
                            iso_code = "ko_KR"    
                        if user[6] == "zh-hans":
                            iso_code = "zh_CN"    
                        if user[6] == "zh-hant":
                            iso_code = "zh_TW"
                            
                        language = self.env['res.lang'].search([('iso_code', '=', iso_code)])
                    
                    res_user_exist = self.env['res.users'].search([('login', '=', user[5]), ('user_aid', '=', user[0]), ('user_uid', '=', user[1])])
                    if not res_user_exist:
                        res_user_exist_parent = self.env['res.users'].search([('login', '=', user[5])])
                        if res_user_exist_parent:
                            res_partner_exist = self.env['res.partner'].search([('partner_aid', '=', user[0]), ('partner_uid', '=', user[1])])
                            if not res_partner_exist:
                                if user[0] != '""':
                                    partner_aid = user[0]
                                if user[1] != '""':
                                    partner_uid = user[1]
                                if user[2] != '""':
                                    phone = user[2]
                                if user[10] != '""':
                                    street = user[10]
                                if user[11] != '""':
                                    street1 = user[11]
                                if user[12] != '""':
                                    city = user[12]
                                if user[13] != '""':
                                    zip_id = user[13]
                                if user[9] != '""':
                                    if user[9] == "Korea; Republic of":
                                        country_name = "South Korea"
                                    elif user[9] == "Taiwan; (ROC)":
                                        country_name = "Taiwan"
                                    elif user[9] == "Korea; Democratic People's Republic of":
                                        country_name = "North Korea"
                                    elif user[9] == "Hong Kong; (SAR)":
                                        country_name = "Hong Kong"
                                    else:
                                        country_name = user[9]
                                    country_id = self.env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                                    if country_id:
                                        country_id = country_id.id
                                    else:
                                        country_id = False
                                if user[3] != '""':
                                    title = False
                                    title_id = self.env['res.partner.title'].search([('shortcut', '=', user[3])], limit=1)
                                    if title_id:
                                        title = title_id.id
                                    else:    
                                        title_id = self.env['res.partner.title'].create({'name':user[3], 'shortcut':user[3]})
                                        if title_id:
                                            title = title_id.id
                                    title = title
                                if user[7] != '""':
                                    dob = user[7]
                                gender = 'select'
                                if user[8] == 0:
                                    gender = 'female'
                                elif user[8] == 1: 
                                    gender = 'male'
                                else:
                                    gender = 'select'
                                gender = gender
                                
                                # // creates new partners as a child of the users
                                res_partner = self.env['res.partner'].create({
                                                                            'firstname':user[14],
                                                                            'lastname':user[15],
                                                                            'partner_aid': partner_aid,
                                                                            'partner_uid':partner_uid,
                                                                            'phone':phone,
                                                                            'street':street,
                                                                            'street1':street1,
                                                                            'city':city,
                                                                            'country_id':country_id,
                                                                            'zip':zip_id,
                                                                            'dob':dob or False,
                                                                            'gender':gender,
                                                                            'title':title,
                                                                            'email':user[5],
                                                                            'parent_id':res_user_exist_parent.partner_id.id,
                                                                            'lang':res_user_exist_parent.partner_id.lang,
                                                                            'exported_country_code':user[16] or False
                                                                            })
                            
                            else:
                                # // Updates the partners
                                if user[0] != '""':
                                    partner_aid = user[0]
                                if user[1] != '""':
                                    partner_uid = user[1]
                                if user[2] != '""':
                                    phone = user[2]
                                if user[10] != '""':
                                    street = user[10]
                                if user[11] != '""':
                                    street1 = user[11]
                                if user[12] != '""':
                                    city = user[12]
                                if user[13] != '""':
                                    zip_id = user[13]
                                if user[9] != '""':
                                    if user[9] == "Korea; Republic of":
                                        country_name = "South Korea"
                                    elif user[9] == "Taiwan; (ROC)":
                                        country_name = "Taiwan"
                                    elif user[9] == "Korea; Democratic People's Republic of":
                                        country_name = "North Korea"
                                    elif user[9] == "Hong Kong; (SAR)":
                                        country_name = "Hong Kong"
                                    else:
                                        country_name = user[9]
                                    country_id = self.env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                                    if country_id:
                                        country_id = country_id.id
                                    else:
                                        country_id = False
                                if user[3] != '""':
                                    title = False
                                    title_id = self.env['res.partner.title'].search([('shortcut', '=', user[3])], limit=1)
                                    if title_id:
                                        title = title_id.id
                                    else:    
                                        title_id = self.env['res.partner.title'].create({'name':user[3], 'shortcut':user[3]})
                                        if title_id:
                                            title = title_id.id
                                    title = title
                                if user[7] != '""':
                                    dob = user[7]
                                gender = 'select'
                                if user[8] == 0:
                                    gender = 'female'
                                elif user[8] == 1: 
                                    gender = 'male'
                                else:
                                    gender = 'select'
                                gender = gender
                                
                                
                                res_partner_exist.first_name =user[14]
                                res_partner_exist.lastname =user[15]
                                res_partner_exist.partner_aid =partner_aid
                                res_partner_exist.partner_uid =partner_uid
                                res_partner_exist.phone =phone
                                res_partner_exist.street =street
                                res_partner_exist.street1 =street1
                                res_partner_exist.city =city
                                res_partner_exist.zip =zip_id
                                res_partner_exist.country_id =country_id
                                res_partner_exist.dob =dob or False
                                res_partner_exist.gender =gender
                                res_partner_exist.title =title
                                res_partner_exist.email =user[5]
                                res_partner_exist.parent_id =res_user_exist_parent.partner_id.id
                                res_partner_exist.lang =res_user_exist_parent.partner_id.lang
                                res_partner_exist.exported_country_code = user[16] or False
                        else:
                            if language:
                                language_code = language.code
                            else:
                                language_code = "en_US"
                            
                            template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id', 'False'))
                            template_user = self.env['res.users'].browse(template_user_id)
                            # // creates new users
                            values = ({'firstname':user[14], 'lastname':user[15], 'login':user[5], 'user_aid': user[0], 'user_uid':user[1], 'lang':language_code})
                            values['active'] = True
                            res_user = template_user.with_context(no_reset_password=False).copy(values)
                            
                            # // writes the value to the created partner of the user
                            if res_user:
                                if user[0] != '""':
                                    res_user.partner_id.partner_aid = user[0]
                                if user[1] != '""':
                                    res_user.partner_id.partner_uid = user[1]
                                if user[2] != '""':
                                    res_user.partner_id.phone = user[2]
                                if user[10] != '""':
                                    res_user.partner_id.street = user[10]
                                if user[11] != '""':
                                    res_user.partner_id.street1 = user[11]
                                if user[12] != '""':
                                    res_user.partner_id.city = user[12]
                                if user[13] != '""':
                                    res_user.partner_id.zip = user[13]
                                if user[9] != '""':
                                    if user[9] == "Korea; Republic of":
                                        country_name = "South Korea"
                                    elif user[9] == "Taiwan; (ROC)":
                                        country_name = "Taiwan"
                                    elif user[9] == "Korea; Democratic People's Republic of":
                                        country_name = "North Korea"
                                    elif user[9] == "Hong Kong; (SAR)":
                                        country_name = "Hong Kong"
                                    else:
                                        country_name = user[9]
                                    country_id = self.env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                                    res_user.partner_id.country_id = country_id.id
                                if user[3] != '""':
                                    title = False
                                    title_id = self.env['res.partner.title'].search([('shortcut', '=', user[3])], limit=1)
                                    if title_id:
                                        title = title_id.id
                                    else:    
                                        title_id = self.env['res.partner.title'].create({'name':user[3], 'shortcut':user[3]})
                                        if title_id:
                                            title = title_id.id
                                    res_user.partner_id.title = title
                                if user[7] != '""':
                                    res_user.partner_id.dob = user[7]
                                gender = 'select'
                                if user[8] == 0:
                                    gender = 'female'
                                elif user[8] == 1: 
                                    gender = 'male'
                                else:
                                    gender = 'select'
                                res_user.partner_id.gender = gender
                                res_user.partner_id.email = user[5]
                                res_user.partner_id.exported_country_code = user[16] or False
                                
                    else:
                        # // Updates the values to the existing users
                        if user[0] != '""':
                            res_user_exist.partner_id.partner_aid = user[0]
                        if user[1] != '""':
                            res_user_exist.partner_id.partner_uid = user[1]
                        if user[2] != '""':
                            res_user_exist.partner_id.phone = user[2]
                        if user[10] != '""':
                            res_user_exist.partner_id.street = user[10]
                        if user[11] != '""':
                            res_user_exist.partner_id.street1 = user[11]
                        if user[12] != '""':
                            res_user_exist.partner_id.city = user[12]
                        if user[13] != '""':
                            res_user_exist.partner_id.zip = user[13]
                        if user[9] != '""':
                            if user[9] == "Korea; Republic of":
                                country_name = "South Korea"
                            elif user[9] == "Taiwan; (ROC)":
                                country_name = "Taiwan"
                            elif user[9] == "Korea; Democratic People's Republic of":
                                country_name = "North Korea"
                            elif user[9] == "Hong Kong; (SAR)":
                                country_name = "Hong Kong"
                            else:
                                country_name = user[9]
                            country_id = self.env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                            res_user_exist.partner_id.country_id = country_id.id
                        if user[3] != '""':
                            title = False
                            title_id = self.env['res.partner.title'].search([('shortcut', '=', user[3])], limit=1)
                            if title_id:
                                title = title_id.id
                            else:    
                                title_id = self.env['res.partner.title'].create({'name':user[3], 'shortcut':user[3]})
                                if title_id:
                                    title = title_id.id
                            res_user_exist.partner_id.title = title
                        if user[7] != '""':
                            res_user_exist.partner_id.dob = user[7]
                        gender = 'select'
                        if user[8] == 0:
                            gender = 'female'
                        elif user[8] == 1: 
                            gender = 'male'
                        else:
                            gender = 'select'
                        res_user_exist.partner_id.gender = gender
                        res_user_exist.partner_id.email = user[5]
                        res_user_exist.partner_id.exported_country_code = user[16] or False


# // Wizard to import the csv file for rewards
class BaseRewardImport(models.TransientModel):
    _name = "base.reward.import"
    _description = "Sales Rewards Import"

    file_import = fields.Binary('File', required=True, attachment=True)
    filename = fields.Char('File Name', required=True)

# // Button action to import rewards
#     @api.multi
    def import_rewards(self):
        if self.file_import:
            # // Extraction of data from the csv file
            file_value = self.file_import.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import a 'csv' file")
            input_file = base64.b64decode(file_value)
            lst = []
            for loop in input_file.decode("utf-8").split("\n"):
                l = loop.replace(u'\ufeff', '')
                vals = l.replace('\r', '')
                lst.append([vals])
            
            # // Deletes the heading of the csv file
            lst.pop(0)
            
            # // Creates the sales rewards
            expiry_date = False
            reward_date = False
            for res in lst:
                if res[0]:
                    reward = res[0].split(',')
                    # // converts unix date to normal date
                    reward_date = ('{}-{}-{} {}:{}:{}'.format(*gmtime(int(reward[2]))))
                    if reward[3]:
                        expiry_date = ('{}-{}-{} {}:{}:{}'.format(*gmtime(int(reward[3]))))
                    else:
                        expiry_date = date.today() + datetime.timedelta(days=30)
                        
                    user = self.env['res.users'].search([('user_uid', '=', reward[1])])
                    if user:
                        sale_reward_exist = self.env['reward.expire'].search([('reward_id', '=', reward[0]), ('reward_uid', '=', reward[1])])
                        if not sale_reward_exist:
                            sale_reward = self.env['reward.expire'].create({
                                                                        'partner_id':user.partner_id.id,
                                                                        'reward_id':reward[0],
                                                                        'reward_expire_date':expiry_date,
                                                                        'reward_date':reward_date,
                                                                        'reward_uid':reward[1],
                                                                        'reward_point':reward[4],
                                                                        })
                        else:
                            print(sale_reward_exist.partner_id.name, "line 242")
#                             raise UserError(_('The Reward for %s already exists!') % (sale_reward_exist.partner_id.name or ""))
