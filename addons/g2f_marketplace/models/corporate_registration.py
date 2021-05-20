# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from datetime import datetime
import base64
from odoo import models, fields, api

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    GROSS_INCOME = [
        ('LOCAL', 'Opero en una sola provincia.'),
        ('SIMPLIFICADO', 'Soy un peque;o contribuyente que realiza actividades en una sola provincia.'),
        ('MULTILATERAL', 'Opero en mas de una provincia.')
    ]

    is_exempt_iva = fields.Boolean(default=False)
    is_exclution_iva = fields.Boolean(default=False)
    is_permanent_exclution = fields.Boolean(default=False)
    certificate_date_start = fields.Date()
    certificate_date_end = fields.Date()
    certificate_file = fields.Binary(string="Certificate File", attachment=True)
    #certificate_file_exc = fields.Binary(string="Certificate Exclution File", attachment=True)
    ## El campo certificate_file_exc se crea por solicitud de @jendelcas hay otro campo igual en la vista
    regime_gross_income = fields.Selection(GROSS_INCOME)
    registration_number_gross_income = fields.Char(
        string='registration number in gross income tax')
    registration_gross_income_file = fields.Binary(
        string="Registration Form File", attachment=True)

    seller_code = fields.Char('Seller code')

    @api.model
    def create(self, vals):
        if vals.get('email'):
            vals['vat'] = vals['email']
            vals['email'] = ''
        return super(ResPartner, self).create(vals)

    def approve(self):
        self.ensure_one()
        if self.seller:
            if not self.seller_code:
                seq = self.env["ir.sequence"].next_by_code("seller.code")
                self.sudo().write({"seller_code": seq})
        self.sudo().write({"state": "approved"})