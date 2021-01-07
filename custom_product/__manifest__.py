# -*- coding: utf-8 -*-

{
    "name": "Custom Product",
    'version': '14.0',
    'category': 'Product',
    'sequence': 14,
    'author':  'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com/',
    'license': 'AGPL-3',
    'summary': 'Product template changes and website product changes',
    "description": """
Product Website
=====================
Product template changes and website product changes

    """,
    "depends": [
        "product",'website','base','sale','website_sale','website_sale_coupon',
    ],
    'external_dependencies': {
    },
    "data": [
        'data/ir_cron.xml',
        'views/product_website_view.xml',
        'static/xml/assets.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    "installable": True,
    'auto_install': False,
    'application': True,
}
