# -*- coding: utf-8 -*-
{
  "name":  "G2F FE Custom",
  "summary":  """Personalización para la facturación electrónica de G2F""",
  "category": "Account",
  "version":  "14.0.2",
  "author":  "kelvis pernia / Andy Quijada",
  "description":  """Módulo de personalización para la facturación electrónica de G2F""",
  "depends":  ['account', 'g2f_marketplace', 'g2f_seller_invoice', 'l10n_ar_edi', 'odoo_marketplace', 'odoo_marketplace_custom'],
  "data":  [
      "security/ir.model.access.csv",
      "views/res_partner_view.xml",
      "views/account_move_view.xml",
            ],
  "application":  False,
  "installable":  True,
  "auto_install":  False,
}
