# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom G2F Argentinian Accounting Reports',
    'category': 'Account',
    'summary': 'Reporting for Argentinian Localization',
    'author': "MiniGO",
    'website': "go2future.com.ar",
    'contributors': ["Boris Silva <silvaboris@gmail.com>"],

    'depends': [
        'base',
        'account',
        'l10n_ar_reports',
    ],
    'data': [
        # 'security/ir.model.access.csv'
        'report/account_ar_vat_line_views.xml',
    ],
    'application': False,
}
