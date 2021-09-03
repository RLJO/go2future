# -*- coding: utf-8 -*-

from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import time
import requests
import json
import logging
_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    location_parent_id = fields.Many2one('stock.location', _('Parent Location'), compute='_compute_stock_parent_location', store=True)
    seller_id = fields.Many2one('res.partner', _('Marketplace Seller'), compute='_compute_stock_marketplace_seller', store=True)

    @api.depends('product_id')
    def _compute_stock_marketplace_seller(self):
        for record in self:
            if record.product_id and record.product_id.marketplace_seller_id:
                record.seller_id = record.product_id.marketplace_seller_id.id
            else:
                record.seller_id = False

    @api.depends('location_id')
    def _compute_stock_parent_location(self):
        for record in self:
            if record.location_id and record.location_id.location_id:
                record.location_parent_id = record.location_id.location_id.id
            else:
                record.location_parent_id = False
