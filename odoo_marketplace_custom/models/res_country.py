# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Country(models.Model):
    _inherit = 'res.country'

    code_mini = fields.Char(string='Código MiniGO')

class CountryState(models.Model):
    _inherit = "res.country.state"

    code_mini = fields.Char(string='Código MiniGO')
