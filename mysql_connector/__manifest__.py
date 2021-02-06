# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mysql Connector',
    'version': '1.1',
    'category': 'Company',
    'summary': 'This module integrate Mysql',
    'description': """
                This module integrate Mysql.
    """,
    "author": "PPTS [India] Pvt.Ltd.",
    'website': 'www.pptssolutions.com',
    'depends': ['base','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/mysql_connector_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'license'		: 'LGPL-3',
	# 'images'		: ['static/description/banner.gif'],
}