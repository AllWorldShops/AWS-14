# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Hide Price",
    "version": "14.0.1.0.0",
    "category": "Website",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "summary": "Hide product prices on the shop",
    "depends": [
        "theme_clarico_vega",
        "website_sale"],
    "data": [
        "views/website_view.xml",
        "views/website_sale_template.xml"],
    "installable": True,
    "application": True
}
