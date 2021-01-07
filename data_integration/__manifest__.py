# -*- encoding: utf-8 -*-
{
    'name': 'Data integration',
    'version': '14.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'sale',
    'description': """This module allows you to integrate with another database which have the required fields.""",
    'summary':"Database Integration between two databases in ODOO.",
    'depends': ['base', 'product','account','emipro_theme_base','website_sale'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/data_integration.xml',
        'data/create_product_cron.xml',
        ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
