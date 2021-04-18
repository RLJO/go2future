# Copyright 2020 FoxCarlos
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "G2F Marketplace",
    'summary': """
        Go2future Inherit Marketplace""",
    'author': "FoxCarlos, Odoo Community Association (OCA)",
    'website': "go2future.com.ar",
    'category': 'sale',
    'license': 'LGPL-3',
    'version': '14.0.1.0.0',
    'depends': ['contacts', 'website', 'website_sale', 'odoo_marketplace'],
    'data': [
        'security/ir.model.access.csv',
        'templates/sellers_registration_template.xml',
        'templates/message_ok_template.xml',
        'templates/warning_template.xml',
        'views/sellers_registration_view.xml',
        'views/seller_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
