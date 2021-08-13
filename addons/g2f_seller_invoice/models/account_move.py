# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    einvoice = fields.Char('Invoice number')
    date_einvoice = fields.Datetime('Invoice date')
    cae_number = fields.Char('CAE number')
    ei_qr_code = fields.Char('QR code')
    ei_barcode = fields.Binary('Invoice barcode')
    ei_xml_file = fields.Text('XML file')
    ei_pdf = fields.Binary('PDF invoice')
    seller_respond = fields.Text('Seller respond')
    json_sent = fields.Text('JSON sent')

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
                'name': vals['einvoice'],
                'date_einvoice': vals['date_einvoice'],
                'invoice_date': vals['date_einvoice'],
                'cae_number': vals['cae_number'],
                'ei_qr_code': vals['ei_qr_code'],
                # 'ei_barcode': vals['ei_barcode'],
                'ei_xml_file': vals['ei_xml_file'],
                'ei_pdf': vals['ei_pdf']
            })
            inv_id.action_post()
            res = {'AUTHORIZED': 200}
        return res

    def _get_address(self, partner_id):
        address = partner_id.street + ', ' if partner_id.street else ''
        address += partner_id.street2 + ', ' if partner_id.street2 else ''
        address += partner_id.city + ', ' if partner_id.city else ''
        address += partner_id.state_id.name + ', ' if partner_id.state_id.name else ''
        address += 'CP: ' + partner_id.zip + ', ' if partner_id.zip else ''
        address += partner_id.country_id.name if partner_id.country_id.name else ''
        return address

    def json_resend(self):
        sale_obj = self.env['sale.order']
        res = sale_obj.send_api_data(self)
        return res