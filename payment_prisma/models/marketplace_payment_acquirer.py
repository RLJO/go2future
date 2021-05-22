# -*- coding: utf-8 -*-

from odoo import _, fields, models

class MarketplacePaymentAcquirer(models.Model):
    _name = 'marketplace.payment.acquirer'

    name = fields.Char(string=_('Acquierer Name'), required=True)
    sandbox_url = fields.Char(string=_('Sandbox URL'), required=True)
    production_url = fields.Char(string=_('Production URL'), required=True)
    public_key = fields.Char(string=_('Public Key'))
    private_key = fields.Char(string=_('Private Key'))
    state = fields.Selection(selection=[
        ('disabled', _('Disabled')),
        ('sandbox', _('Sandbox')),
        ('production', _('Production'))
    ], string=_('State'), default='disabled')

    def change_state(self):
        self.ensure_one()
        if self.state == 'disabled':
            self.state = 'sandbox'
        elif self.state == 'sandbox':
            self.state = 'production'
        else:
            self.state = 'disabled'


