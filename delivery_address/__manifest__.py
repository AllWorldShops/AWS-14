# -*- coding: utf-8 -*-
{
    'name': 'Delivery Address Popup',
    'version': '13.0',
    'category': 'Website',
    'summary': """This module shows the a pop up to add or select the delivery address.""",
    'description': """
       This module shows address in at the top of the page.
   
   Configuration:
      Installing this module shows shipping address in shop product page and also shows menu to change shipping address.By clicking change address shows some more address which is stored in res_partner by chosing new address will change shipping address as newly selected one
       """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'website', 'sale_coupon', 'website_sale','website_sale_coupon','sale_product_configurator'],
    'data': [
        'views/delivery_address_popup_view.xml',
        'views/popup_template.xml'
        
    ],
    'installable': True,
    'application':True,
    'active': False,
}

