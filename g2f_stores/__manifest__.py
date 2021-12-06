# -*- coding: utf-8 -*-
{
    'name': "g2f_stores",

    'summary': """
        Configuración y gestión de tiendas G2F""",

    'description': """
        Configuración y gestión de tiendas G2F
    """,

    "author":  "Rafael Andara",
    "contributors": ["Rafael Andara <randarad@gmail.com>"],
    'website': "https://www.minigo.store/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/door_view.xml',
        'views/camera_view.xml',
        'views/sensor_store.xml',
        'views/raspi_views.xml',
        'views/zone_camera_view.xml',
        'views/zone_camera_points.xml',
        'views/store_iaserver.xml',
        'views/plano_product_view.xml',
        'views/templates.xml',
        'views/store_images.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
