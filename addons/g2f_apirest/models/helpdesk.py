# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except
# -

import logging
from odoo import models, fields


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'helpdesk.ticket'

    phone = fields.Char(string='Phone')
