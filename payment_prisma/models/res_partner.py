# -*- coding: utf-8 -*-

from odoo import _, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    prisma_user_id = fields.Char(string=_('User ID'))
    site_ids = fields.Char(string=_('Site ID'))
    payment_cards_ids = fields.One2many(comodel_name='payment.cards', inverse_name='partner_id', string=_('Payment Cards'))
