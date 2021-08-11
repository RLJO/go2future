# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from OpenSSL import crypto

import base64
import logging
import random
import re

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super(SaleOrder, self)._create_invoices(grouped, final, date)
        for move in moves:
            move.company_invoicing = False
            if move.seller_id and move.seller_id.fe_journal_id:
                move.journal_id = move.seller_id.fe_journal_id
            if move.seller_id.electronic_invoice_type in ['afip', 'no_afip']:
                move.action_post()
        return moves