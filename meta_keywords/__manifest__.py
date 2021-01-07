# -*- coding: utf-8 -*-
{
    'name': 'Meta Keywords',
    'version': '14.0',
    'category': 'Website',
    'summary':"""This module adds new page called optimize in product template to provide meta tags and meta keywords
      to each products  """,
    'description': """
       This module adds meta tags/keywords in product templates.
   
   Configuration:
      Installing this module adds new page called optimize in product template to provide meta tags and meta keywords
      to each products      
      
       """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'sale', 'product', 'website'],
    'data': [
        
        'views/product_template_inherited_view.xml'
        
    ],
    'installable': True,
    'application':True,
    'active': False,
}

