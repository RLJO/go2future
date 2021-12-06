# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    price = fields.Float(string=_('Price'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    store_id = fields.Many2one('stock.warehouse', string=_('Tienda'), related='order_id.warehouse_id', store=True)
