# -*- coding: utf-8 -*-
{
    'name': 'Custom Website',
    'version': '14.0',
    'category': 'Website',
    'summary': 'This module customizes the website shop page.',
    'description': """
       This module allows you to customize the views of the website shop page along with the theme clarico module.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'web', 'website', 'emipro_theme_base', 'theme_clarico_vega', 'website_sale', 'payment', 'website_sale_delivery','sale'],
    'data': [
        
    'views/custom_website_view.xml',
    'views/custom_assets.xml',
    'views/sale_order_views.xml',
    'views/sale_order_mail_template.xml',
    
        
    ],
    'installable': True,
    'application':True,
    'active': False,
}

