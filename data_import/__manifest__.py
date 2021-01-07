# -*- coding: utf-8 -*-
{
    'name': 'Data Import',
    'version': '14.0',
    'category': 'Settings',
    'description': """The datas exported from the magento database could be imported to Odoo using this module.
       """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'summary': 'Imports datas of Users and Webit points from magento server',
    'depends': ['base', 'mail', 'partner_firstname','product'],
    'data': [
        'data/ir_cron.xml',
        'views/res.xml',
        'views/data_import.xml',
    ],
    'installable': True,
    'application':True,
    'active': False,
}

