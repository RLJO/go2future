# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
import json
from datetime import datetime
from odoo import models, fields


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class Transaction(models.Model):
    _name = 'apirest.transaction'
    _description = 'transaction messages'

    login = fields.Char()
    store_id = fields.Char()
    door_id = fields.Char()
    code = fields.Char()
    message = fields.Char()
    from_app = fields.Char()
    datetime = fields.Datetime('Scheduled Date', default=fields.Datetime.now)
    active = fields.Boolean(default=True)

    def parse_dumps(self, object):
        """Parse fields for dumps response."""

        if isinstance(object, datetime):
            return object.__str__()

        if isinstance(object, bytes):
            return object.decode('ascii') 

    def get_last_transaction_by_user(self, login):
        """Get las transacction by user."""

        transaction = self.env['apirest.transaction'].search_read(
                [('login', '=', login), ('active', '=', True)],
                ['login', 'store_id', 'door_id', 'datetime'],
                order="datetime desc", limit=1)

        _logger.info(transaction)
        return transaction

    def get_transaction_by_user(self, login='', store_id=''):
        """return transaction list by user passed."""

        domain = [('login', '=', login),
                  ('store_id', '=', store_id),
                  ('active', '=', True)
                  ]
        trasaction_list = self.search_read(
            domain,
            ['login', 'code', 'message', 'from_app']
        )
        if trasaction_list:
            self.mark_transaction_as_seen(domain)
        return json.dumps(trasaction_list)

    def create_transaction(self, login='', store_id='', door_id='', code='',
                           message='', from_app=''):
        """Create transactions LOG."""

        values = {'login': login,
                  'store_id': store_id,
                  'door_id': door_id,
                  'code': code,
                  'message': message,
                  'from_app': from_app}

        transaction_instance = self.create(values)
        transaction_instance._cr.commit()
        return True

    def mark_transaction_as_seen(self, transaction_domain):
        """Mark transaction as seem."""
        if transaction_domain:
            transaction_instance = self.search(transaction_domain)
            transaction_instance.write({'active': False})
            transaction_instance._cr.commit()
            return True
        return False
