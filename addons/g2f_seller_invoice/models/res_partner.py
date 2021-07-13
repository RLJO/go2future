# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    seller_api_path = fields.Char(string='Seller API path')
    seller_api_key = fields.Char(string='Seller API Key')