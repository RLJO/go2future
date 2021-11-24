# Copyright 2020 FoxCarlos
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "G2F Api Rest",
    'summary': """
        Go2future App Mobile""",
    'author': "FoxCarlos, Odoo Community Association (OCA)",
    'website': "http://redti.naltu.com",
    'category': 'ecommerce',
    'license': 'LGPL-3',
    'version': '12.0.1.0.0',
    'depends': ['website', 'website_sale', 'l10n_ar', 'payment_prisma', 'g2f_stores'],
    'data': [
        'views/res_partner_views.xml',
        'views/helpdesk.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
