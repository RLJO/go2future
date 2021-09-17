# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date


class L10nARVatBook(models.AbstractModel):
    _inherit = "l10n_ar.vat.book"

    def _get_columns_name(self, options):
        if not options.get('journal_type'):
            options.update({'journal_type': self.env.context.get('journal_type', 'sale')})
        dynamic_columns = [item.get('name') for item in self._get_dynamic_columns(options)]
        return [
            {'name': _("Date"), 'class': 'date'},
            {'name': _("Document"), 'class': 'text-left'},
            {'name': _("Name"), 'class': 'text-left'},
            {'name': _("Accounting Account"), 'class': 'text-left'},
            {'name': _("Vat Cond."), 'class': 'text-left'},
            {'name': _("VAT"), 'class': 'text-left'},
            {'name': _('Taxed'), 'class': 'number'},
            {'name': _('Not Taxed'), 'class': 'number'},
        ] + [{'name': item, 'class': 'number'} for item in dynamic_columns] + [
            {'name': _('VAT 10,5%'), 'class': 'number'},
            {'name': _('VAT 21%'), 'class': 'number'},
            {'name': _('VAT 27%'), 'class': 'number'},
            {'name': _('VAT Perc'), 'class': 'number'},
            {'name': _('Other Taxes'), 'class': 'number'},
            {'name': _('Total'), 'class': 'number'},
        ]

    @api.model
    def _get_lines(self, options, line_id=None):
        journal_type = options.get('journal_type')
        if not journal_type:
            journal_type = self.env.context.get('journal_type', 'sale')
            options.update({'journal_type': journal_type})
        lines = []
        line_id = 0
        sign = 1.0 if journal_type == 'purchase' else -1.0
        domain = self._get_lines_domain(options)

        dynamic_columns = [item.get('sql_var') for item in self._get_dynamic_columns(options)]
        totals = {}.fromkeys(['taxed', 'not_taxed'] + dynamic_columns + ['vat_10', 'vat_21', 'vat_27', 'vat_per', 'other_taxes', 'total'], 0)
        for rec in self.env['account.ar.vat.line'].search_read(domain):
            taxed = rec['base_25'] + rec['base_5'] + rec['base_10'] + rec['base_21'] + rec['base_27']
            other_taxes = rec['other_taxes']
            totals['taxed'] += taxed
            totals['not_taxed'] += rec['not_taxed']
            for item in dynamic_columns:
                totals[item] += rec[item]
            totals['vat_10'] += rec['vat_10']
            totals['vat_21'] += rec['vat_21']
            totals['vat_27'] += rec['vat_27']
            totals['vat_per'] += rec['vat_per']
            totals['other_taxes'] += other_taxes
            totals['total'] += rec['total']

            lines.append({
                'id': rec['id'],
                'name': format_date(self.env, rec['invoice_date']),
                'class': 'date' + (' text-muted' if rec['state'] != 'posted' else ''),
                'level': 2,
                'model': 'account.ar.vat.line',
                'caret_options': 'account.move',
                'columns': [
                    {'name': rec['move_name']},
                    {'name': rec['partner_name']},
                    {'name': rec['account_name']},
                    {'name': rec['afip_responsibility_type_name']},
                    {'name': rec['cuit']},
                    {'name': self.format_value(sign * taxed)},
                    {'name': self.format_value(sign * rec['not_taxed'])},
                    ] + [
                        {'name': self.format_value(sign * rec[item])} for item in dynamic_columns] + [
                    {'name': self.format_value(sign * rec['vat_10'])},
                    {'name': self.format_value(sign * rec['vat_21'])},
                    {'name': self.format_value(sign * rec['vat_27'])},
                    {'name': self.format_value(sign * rec['vat_per'])},
                    {'name': self.format_value(sign * other_taxes)},
                    {'name': self.format_value(sign * rec['total'])},
                ],
            })
            line_id += 1

        lines.append({
            'id': 'total',
            'name': _('Total'),
            'class': 'o_account_reports_domain_total',
            'level': 0,
            'columns': [
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(sign * totals['taxed'])},
                {'name': self.format_value(sign * totals['not_taxed'])},
                ] + [
                    {'name': self.format_value(sign * totals[item])} for item in dynamic_columns] + [
                {'name': self.format_value(sign * totals['vat_10'])},
                {'name': self.format_value(sign * totals['vat_21'])},
                {'name': self.format_value(sign * totals['vat_27'])},
                {'name': self.format_value(sign * totals['vat_per'])},
                {'name': self.format_value(sign * totals['other_taxes'])},
                {'name': self.format_value(sign * totals['total'])},
            ],
        })

        return lines