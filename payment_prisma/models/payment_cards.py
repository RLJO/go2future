# -*- coding: utf-8 -*-

from datetime import date, timedelta
from odoo import _, api, fields, models

MONTHS = [
    ('01', _('January')),
    ('02', _('February')),
    ('03', _('March')),
    ('04', _('April')),
    ('05', _('May')),
    ('06', _('June')),
    ('07', _('July')),
    ('08', _('August')),
    ('09', _('September')),
    ('10', _('October')),
    ('11', _('November')),
    ('12', _('Dicember'))
]

class PaymentCards(models.Model):
    _name = 'payment.cards'

    def _get_expiration_years(self):
        years = []
        for i in range(30):
            years.append((str(date.today().year + i), str(date.today().year + i)))
        return years

    name = fields.Char(string=_('Card Description'), required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string=_('Card Holder'), required=True)
    card_number = fields.Char(string=_('Card Number'), required=True)
    security_code = fields.Char(string=_('Security Code'), required=True)
    expiration_month = fields.Selection(selection=MONTHS, string=_('Expiration Month'), default='01', required=True)
    expiration_year = fields.Selection(selection=_get_expiration_years, string=_('Expiration Year'), required=True)
    card_type = fields.Selection(selection=[
        ('credit', _('Credit')),
        ('debit', _('Debit'))
    ], string='Card Type', default='credit')
    card_identification = fields.Many2one(comodel_name='payment.cards.types', string='Card Identification', domain="[('type', '=', card_type)]")
    state = fields.Selection(selection=[
        ('disabled', _('Disabled')),
        ('active', _('Active'))
    ], default='disabled')
    card_last_digits = fields.Char(string=_('Last Digits'), compute='_compute_last_digits')

    @api.depends('card_number')
    def _compute_last_digits(self):
        for record in self:
            if len(record.card_number) >= 4:
                record.card_last_digits = record.card_number[-4:]

    def change_state(self):
        self.ensure_one()
        if self.state == 'disabled':
            self.state = 'active'
        else:
            self.state = 'disabled'


    def activate_card(self):
        partner = self.partner_id
        if partner:
            for card in partner.payment_cards_ids:
                card.state = 'disabled'
        self.state = 'active'

    def disable_card(self):
        self.state = 'disabled'

class PaymentCardsTypes(models.Model):
    _name = 'payment.cards.types'

    name = fields.Char(string=_('Name'))
    payment_method_id = fields.Integer(string=_('Payment Method ID'))
    type = fields.Selection(selection=[
        ('credit', _('Credit')),
        ('debit', _('Debit'))
    ], string='Type')



