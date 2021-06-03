# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Customize Bundle Products",
  "summary"              :  """The module allows the admin to create bundles of products on the Odoo website and sell those products in a bundled form.""",
  "category"             :  "Website",
  "version"              :  "5.2.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Customize-Bundle-Products.html",
  "description"          :  """Odoo website Customized Bundle Products
Odoo website Product Pack
Odoo product packaging
Odoo product pack
product package in Odoo
website packs
make bundled products
bundled products website
Odoo website Product packages
create Product bundles Odoo
website Product bundles
Odoo website
Odoo multi vendor website
Manage Packages
Product Package
Wholesale Product
Wholesale Management
Dynamic Bundle Produts
Customize Bundle Products
Customize Pack Products
Dynamic Pack products""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=dynamic_bundle_products&version=14.0",
  "depends"              :  [
                             'website_sale',
                             'stock',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/dynamic_bundle_products_view.xml',
                             'wizard/dynamic_bundle_product_wizard_view.xml',
                             'views/templates.xml',
                             'views/res_config_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                            #  'data/website_product_pack_data.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  112,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}