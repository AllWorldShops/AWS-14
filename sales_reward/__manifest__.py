# -*- coding: utf-8 -*-
{
    'name': "Rewards/Loyalty Points for POS & Website",

    'summary': """
        Sales Reward Module creates reward points for each customer and adds the points on each paid amount of sales invoice.
        """,

    'description': """
        - Reward Percentage and Redeem Percentage values are set in the Reward Settings under Sales --> Configuration menu.

        - Rewards points are calculated for each sales invoice's paid amount(as per the set values) and displayed in Reward points column in Customer module. 

        - Total Reward Points are displayed for the individual customer.

        - If customer want to use the points, converted amount of Total Reward Points is then deducted from the total invoiced amount.
        """,
    'price': 70.00,
    'currency': 'EUR',
    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",
    'license':'OPL-1',
    'category': 'Sales',
    'version': '0.2',

    'depends': ['base', 'sale', 'sale_management','sales_team','point_of_sale','website_sale', 'mail',],

    'data': [
        'views/sales_order.xml',
        'views/rewards_res_config_settings.xml',
        'views/res_partner.xml',
        'views/account_invoice.xml',
        'views/sale_order_report.xml',
        'views/account_invoice_report.xml',
        'views/pos_view.xml',
        'views/website_order.xml',
        'views/custom_mail.xml',
        'views/schedular.xml',
        'views/loyalty_menu_sale.xml',
        'views/loyalty_menu_pos.xml',
        'views/website_access.xml',
        'report/loyality_card_print_report.xml',
        'views/mail_template.xml',
    ],

    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'images': [
        'images/main.png',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
