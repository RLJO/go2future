# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    warehouse_id = fields.Many2one('stock.warehouse', string=_('Warehouse'))


