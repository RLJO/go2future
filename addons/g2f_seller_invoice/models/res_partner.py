# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    seller_api_path = fields.Char(string='Seller API path')
    seller_api_key = fields.Char(string='Seller API Key')
    seler_token_type = fields.Selection(string='Tipo de Auth', default='bearer',
                                        selection=[('bearer', 'Bearer'), ('header', 'Header-Tag')])
    token_tag = fields.Char(string='Etiqueta')
