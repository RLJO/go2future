# -*- coding: utf-8 -*-
{
    'name': "G2f MINIGO Rest API para vendedores",

    'summary': """
        Rest API para facturación de vendedores a clientes""",

    'description': """
        Rest API para facturación de vendedores a clientes
    """,

    'author': "MiniGO",
    'website': "go2future.com.ar",
    'contributors': ["Boris Silva <silvaboris@gmail.com>"],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'website',
        'website_daily_deals',
        'purchase'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_view.xml',
        # 'wizard/purchase_order_wizard.xml',
    ],
}
