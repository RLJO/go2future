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
  "name":  "G2F Marketplace custom",
  "summary":  """Start your marketplace in odoo with Odoo Multi-Vendor Marketplace custom.""",
  "category": "Website",
  "version":  "14.0.7",
  "author":  "kelvis pernia / Andy Quijada",
  "contributors": ["Boris Silva <silvaboris@gmail.com>"],
  "description":  """Odoo Multi Vendor Marketplace custom""",
  "depends":  ['base', 'l10n_latam_base', 'sale', 'odoo_marketplace', 'marketplace_seller_wise_checkout',
               'g2f_marketplace', 'account', 'g2f_stores', 'stock', 'l10n_ar'],
  "data":  ['data/marketplace_security_data.xml',
            'security/ir.model.access.csv',
            'views/res_partner_children.xml',
            'views/seller_view_custom.xml',
            'views/products.xml',
            'views/sale_order_views.xml',
            'views/res_country_view.xml',
            'views/stock_view_custom.xml',
            'data/marketplace_dashboard_data.xml',
            'data/cron_data.xml',
            'reports/invoice_report.xml',
            ],
  "application":  True,
  "installable":  True,
  "auto_install":  False,
}
