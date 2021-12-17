# -*- coding: utf-8 -*-
{
    'name': "G2f_user_menu",

    'summary': """
        Cambio de link en menu de usuarios para Documentacion y Soporte""",

    'description': """
        Cambio de link en menu de usuarios para Documentacion y Soporte
    """,

    "author":  "Rafael Andara",
    "contributors": ["Rafael Andara <randarad@gmail.com>"],
    'website': "https://www.minigo.store/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web_enterprise'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/user_menu.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
