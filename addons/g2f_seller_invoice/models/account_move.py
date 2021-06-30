# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    einvoice = fields.Char('Invoice number')
    date_einvoice = fields.Date('Invoice date')
    cae_number = fields.Char('CAE number')
    ei_qr_code = fields.Char('QR code')
    ei_barcode = fields.Binary('Invoice barcode')
    ei_xml_file = fields.Text('XML file')
    ei_pdf = fields.Binary('PDF invoice')

    @api.model
    def _invoice_confirm(self, vals):
        if len(vals) < 7:
            err_msg = "Falta un campo requerido ('einvoice', 'date_einvoice', " \
                      "'cae_number', 'ei_qr_code', 'ei_xml_file', 'ei_pdf')"
            return {'FAILED': 400, 'DESCRIPTION': err_msg}

        inv_obj = self.env['account.move']
        inv_id = inv_obj.search([('id', '=', vals['id']), ('state', '=', 'draft')])
        err_msg = 'No se encontró factura borrador con el id: %s' % vals['id']
        res = {'FAILED': 400, 'DESCRIPTION': err_msg}
        if inv_id:
            inv_id.sudo().write({
                'einvoice': vals['einvoice'],
                'date_einvoice': vals['date_einvoice'],
                'cae_number': vals['cae_number'],
                'ei_qr_code': vals['ei_qr_code'],
                # 'ei_barcode': vals['ei_barcode'],
                'ei_xml_file': vals['ei_xml_file'],
                'ei_pdf': vals['ei_pdf']
            })
            inv_id.action_post()
            res = {'AUTHORIZED': 200}
        return res

    # def action_post(self):
    #     inv_obj = self.env['account.move']
    #     inv_id = inv_obj.search([('id', '=', 1), ('state', '=', 'draft')])
    #     res = 'No se encontró factura borrador con el id: %s' % 1
    #     if inv_id:
    #         inv_id.sudo().write({
    #             'einvoice': 'F001',
    #             'cae_number': '111222333'
    #         })
    #         # inv_id.action_post()
    #         res = 200
    #     return res