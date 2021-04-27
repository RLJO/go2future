# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    einvoice = fields.Char('Invoice number')
    date_einvoice = fields.Date('Invoice date')
    cae_number = fields.Char('CAE number')
    ei_qr_code = fields.Binary('QR code')
    ei_barcode = fields.Binary('Invoice barcode')
    ei_xml_file = fields.Binary('XML file')
    ei_pdf = fields.Binary('PDF invoice')
