# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    seller_code = fields.Char('Seller code')

    def approve(self):
        self.ensure_one()
        if self.seller:
            if not self.seller_code:
                seq = self.env["ir.sequence"].next_by_code("seller.code")
                self.sudo().write({"seller_code": seq})
        self.sudo().write({"state": "approved"})
