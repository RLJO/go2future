# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
import json
import base64


class AccountAfipReport(models.TransientModel):
    _name = 'account.afip.report'
    _description = "Report of invoices issued to the final consumer"

    def make_afip_file(self):
        print('*****************HOLA********************')

        view_move_form = self.env.ref('odoo_marketplace_custom.account_afip_statement_view')
        action = {
            'name': _('AFIP Statement Report'),
            'view_mode': 'form',
            'view_id': view_move_form.id,
            'res_model': 'account.afip.report',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
        }
        return action
