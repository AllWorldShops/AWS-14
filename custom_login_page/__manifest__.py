# -*- encoding: utf-8 -*-

{
    'name': 'Custom Login Page',
    'summary': '',
    'version': '13.0.1.0',
    'category': 'Website',
    'summary': """
       This module applies for the customization for the website login page.
    """,
    'description': """
       This module allows you to customize the login page of the website with change in views.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': [
	'website', 'auth_oauth'
    ],
    'data': [
        'templates/webclient_templates.xml',
    ],
    'installable': True,
    'application': True,
    'active': False,
}
