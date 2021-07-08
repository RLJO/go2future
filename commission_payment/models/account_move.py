# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _commission_confirm_move(self):
        move_id = self.search([])
        journal = self.env['account.journal'].search([('commission', '=', True)])
        move = move_id.filtered(lambda move_id: move_id.journal_id == journal and move_id.state == 'draft')
        for account_move in move:
            account_move.action_post()
            account_move._send_email()

    def _send_email(self):
        if not self.partner_id.email_commission:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))
        template = self.env.ref('commission_payment.email_template_commission')
        for wizard_line in self:
            lang = wizard_line.env.user.lang
            partner = wizard_line.env.user.partner_id

            portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                partner.id]
            partner.signup_prepare()
            if template:
                template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).sudo().send_mail(
                    wizard_line.id, force_send=True)
            else:
                _logger.warning("No email template found for sending email to the portal user")

        return True
