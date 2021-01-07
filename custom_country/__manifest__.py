# -*- coding: utf-8 -*-
{
    'name': 'Country Customization',
    'version': '14.0',
    'category': 'Website',
    'description': """
       This module adds country field.
   
   Configuration:
      Installing this module adds new field called country in sale order,purchase order,delivery order,account invoice.This country fields allows to filter option using country
      
      
       """,
    'summary': """
       This module creates a country field, which allows to filter option using country.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base','sale','purchase','account','stock'],
    'data': [
#         'views/account_invoice_inherited_view.xml',
        'views/purchase_order_inherited_view.xml',
        'views/sale_order_inherited_view.xml',
        'views/stock_picking_inherited_view.xml',
        'views/account_move_inherited_view.xml'
    
        
    ],
    'installable': True,
    'application':True,
    'active': False,
}

