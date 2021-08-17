# -*- coding: utf-8 -*-

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', string=_('Origin'))
    payment_prisma_status_ids = fields.One2many(related='sale_order_id.payment_prisma_status_ids')
