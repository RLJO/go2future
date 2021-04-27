# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    api_path = fields.Char('API path')