# Copyright 2020 FoxCarlos
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "G2F Sale",
    'summary': """
        Go2future Sale""",
    'author': "FoxCarlos, Odoo Community Association (OCA)",
    'website': "",
    'category': 'Sales',
    'license': 'LGPL-3',
    'version': '12.0.1.0.1',
    'depends': ['sale_management', 'purchase', 'stock', 'uom',
                'odoo_marketplace', 'g2f_marketplace'],
    'data': [
        'views/product_template.xml',
        'views/product_template_marketplace.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
