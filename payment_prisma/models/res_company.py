# -*- coding: utf-8 -*-

from odoo import _, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    site_ids = fields.Char(string=_('Código prisma'))
