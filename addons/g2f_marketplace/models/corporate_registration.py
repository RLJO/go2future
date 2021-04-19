# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from datetime import datetime
import base64
from odoo import models, fields

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
    certificate_file = fields.Binary(string="Certificate Exclution File",
                                     attachment=True)
    regime_gross_income = fields.Selection(GROSS_INCOME)
    registration_number_gross_income = fields.Char(
        string='registration number in gross income tax')
    registration_gross_income_file = fields.Binary(
        string="Registration Form File", attachment=True)
