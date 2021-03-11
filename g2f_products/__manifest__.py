# Copyright 2020 Francisco Morosini
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "G2F Products",
    'summary': """
        Go2future Products""",
    'author': "Francisco Morosini",
    'website': "http://redti.naltu.com",
    'category': 'ecommerce',
    'license': 'LGPL-3',
    'version': '12.0.1.0.0',
    'depends': ['website', 'website_sale', 'stock'],
    'data': [        
        'views/product.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
