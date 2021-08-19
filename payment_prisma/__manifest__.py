# -*- coding: utf-8 -*-
{
  "name":  "G2F Payment Prisma",
  "summary":  """Enables the use of the Prisma payment gateway.""",
  "category": "Payment",
  "version":  "1.0.0",
  "contributors": ["Boris Silva <silvaboris@gmail.com>"],
  "author":  "kelvis pernia / Andy Quijada",
  "description":  """Enables the use of the Prisma payment gateway.""",
  "depends":  [
    'account',
    'odoo_marketplace',
    'odoo_marketplace_custom',
    'sale'
  ],
  "data":  [
    'data/marketplace_payment_acquirer_data.xml',
    'data/payment_cards_type_data.xml',
    'security/ir.model.access.csv',
    'views/res_partner_view.xml',
    'views/marketplace_payment_acquirer_view.xml',
    'views/payment_cards_view.xml',
    'views/sale_order_view.xml',
    'views/res_company_view.xml',
    'views/account_move_view.xml',
  ],
  "installable":  True,
  "auto_install":  False,
}
