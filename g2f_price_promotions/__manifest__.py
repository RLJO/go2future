# -*- coding: utf-8 -*-
{
    'name': "g2f_price_promotions",

    'summary': """
        Configuración de Precios y Promociones G2F""",

    'description': """
        Configuración de Precios y Promociones por Vendedores para G2F
    """,

    "author":  "Rafael Andara",
    "contributors": ["Rafael Andara <randarad@gmail.com>"],
    'website': "https://www.minigo.store/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'product', 'odoo_marketplace'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
