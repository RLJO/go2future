# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from odoo import models, fields

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class Transaction(models.Model):
    _name = 'apirest.transaction'
    _description = 'transaction messages'

    login = fields.Char()
    code = fields.Char()
    message = fields.Char()
    from_app = fields.Char()
    datetime = fields.Datetime('Scheduled Date', default=fields.Datetime.now)
    active = fields.Boolean(default=True)

    def get_transaction_by_user(self, login):
        """return transaction list by user passed."""

        domain = [('login', '=', login)]
        trasaction_list = self.search_read(domain)
