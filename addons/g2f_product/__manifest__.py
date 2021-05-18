# -*- coding: utf-8 -*-
{
    'name': "G2F Product",

    'summary': """
        Add catman and nutrition facts pages to product """,

    'description': """
        Add catman and nutrition facts pages to product
    """,

    'author': "Go 2 Future",
    'website': "go2future.com.ar",
    'contributors': ["Boris Silva <silvaboris@gmail.com>"],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'odoo_marketplace', 'g2f_sale'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/product_marketplace.xml',
        'views/group_seller_view.xml',
    ],

}
