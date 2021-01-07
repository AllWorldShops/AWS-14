# -*- coding: utf-8 -*-

{
    "name": "Custom Partner",
    'version': '13.0',
    'category': 'Partner',
    'sequence': 14,
    'author':  'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com/',
    'license': 'AGPL-3',
    'summary': 'Partner Additional Fields',
    "description": """
    New fields added in res_partner
        """,
    "depends": [
       'base'   
    ],
    'external_dependencies': {
    },
    "data": [
        'views/res_partner_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    "installable": True,
    'auto_install': False,
    'application': False,
}
