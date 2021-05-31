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
  "name":  "Odoo Multi Vendor Marketplace custom",
  "summary":  """Start your marketplace in odoo with Odoo Multi-Vendor Marketplace custom.""",
  "category": "Website",
  "version":  "1.0.1",
  "author":  "kelvis pernia / Andy Quijada",
  "description":  """Odoo Multi Vendor Marketplace custom""",
  "depends":  ['base', 'l10n_latam_base', 'sale', 'odoo_marketplace', 'marketplace_seller_wise_checkout',
               'g2f_marketplace', 'account'],
  "data":  ['data/marketplace_security_data.xml',
            'security/ir.model.access.csv',
            'views/res_partner_children.xml',
            'views/seller_view_custom.xml',
            'views/products.xml',
            'views/sale_order_views.xml',
            'data/marketplace_dashboard_data.xml',
            ],
  "application":  True,
  "installable":  True,
  "auto_install":  False,
}
