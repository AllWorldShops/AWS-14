# -*- encoding: utf-8 -*-

{
    'name': 'Custom Brand Page',
    'summary': '',
    'version': '14.0.1.0',
    'category': 'Website',
    'summary': """
       This module shows the brand names of the products listed out in the website.
    """,
    'description': """This module allows you to show the brands of the in the website page with a separate tab in with the
    brand names in a separate page. 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': [
# 	'website', 'website_sale', 'website_stock',
    'website', 'website_sale','emipro_theme_brand','custom_sale','emipro_theme_base'
    ],
    'data': [
        'templates/assets.xml',
        'data/website_data.xml',
        'templates/webclient_templates.xml',
        'templates/price_filter.xml',
    ],
    'installable': True,
    'application': True,
    'active': False,
}
