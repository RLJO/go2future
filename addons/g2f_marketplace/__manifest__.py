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
    'depends': ['contacts', 'website', 'odoo_marketplace'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/seller_view.xml',
        'views/group_seller_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
