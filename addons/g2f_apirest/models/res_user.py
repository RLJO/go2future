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


class ResUser(models.Model):
    _inherit = 'res.users'

    def is_staff(self):
        self.ensure_one()
        return self.employee_id.user_id
