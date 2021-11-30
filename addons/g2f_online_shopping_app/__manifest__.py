# Copyright 2020 FoxCarlos
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "G2F Online Shopping App",
    'summary': """
        Go2future Online Shopping App Mobile""",
    'author': "FoxCarlos, Odoo Community Association (OCA)",
    'website': "",
    'category': 'ecommerce',
    'license': 'LGPL-3',
    'version': '14.0.1.0.0',
    'depends': ['website', 'website_sale', 'l10n_ar', 'payment_prisma', 'g2f_stores'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view_form.xml',
        'views/sale_order_view_search.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
