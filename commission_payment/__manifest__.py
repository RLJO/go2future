# -*- coding: utf-8 -*-
{
  "name":  "G2F commission payment",
  "summary":  """pago comisión mini go.""",
  "category": "payment",
  "version":  "14.0.0",
  "author":  "kelvis pernia / Andy Quijada",
  "description":  """Odoo commission payment""",
  "depends":  ['base', 'sale', 'odoo_marketplace', 'marketplace_seller_wise_checkout', 'account',
               'odoo_marketplace_custom'],
  "data":  [
    'views/account_journal.xml',
    'views/product.xml',
    'data/cron_commission.xml',
    'data/email_data.xml',
            ],
  "application":  True,
  "installable":  True,
  "auto_install":  False,
}
