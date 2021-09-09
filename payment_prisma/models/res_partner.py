# -*- coding: utf-8 -*-

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    prisma_user_id = fields.Char(string=_('User ID'))
    site_ids = fields.Char(string=_('Código prisma'))
    payment_cards_ids = fields.One2many(comodel_name='payment.cards', inverse_name='partner_id', string=_('Payment Cards'))

    def get_active_card(self):
        if len(self.payment_cards_ids):
            active_card = self.payment_cards_ids.filtered(lambda r: r.state == 'active')
            return active_card or False
