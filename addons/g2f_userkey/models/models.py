# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class APIKeyDescription(models.TransientModel):
    _inherit = _description = 'res.users.apikeys.description'

    #@check_identity
    def make_key(self):
        # only create keys for users who can delete their keys
        if not self.user_has_groups('base.group_user') | self.user_has_groups('base.group_portal'):
            raise AccessError(_("Only internal users or Portal users can create API keys"))

        description = self.sudo()
        k = self.env['res.users.apikeys']._generate(None, self.sudo().name)
        description.unlink()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.users.apikeys.show',
            'name': 'API Key Ready',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_key': k,
            }
        }