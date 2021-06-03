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
  "name"                 :  "Odoo Marketplace Customized Bundle Products",
  "summary"              :  """The module allows the admin to create bundles of products on the Odoo marketplace and sell those products in a bundled form.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Customized-Bundle-Products.html",
  "description"          :  """Odoo Marketplace Customized Bundle Products
Odoo Marketplace Product Pack
Odoo product packaging
Odoo product pack
product package in Odoo
Marketplace packs
make bundled products
bundled products marketplace
Odoo marketplace Product packages
create Product bundles Odoo
Marketplace Product bundles
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
Multi-seller marketplace
multi-vendor Marketplace
Manage Packages
Product Package
Wholesale Product
Wholesale Management""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_dynamic_bundle_products&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'odoo_marketplace',
                             'dynamic_bundle_products',
                            ],
  "data"                 :  [
                             'security/access_control_security.xml',
                             'security/ir.model.access.csv',
                             'views/mp_bundle_products_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  35,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}