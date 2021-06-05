# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models,api,fields
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange('marketplace_seller_id')
    def _clear_products_in_pack(self):
        for rec in self:
            rec.wk_bundle_products = []

class ProductPack(models.Model):
    _inherit = "product.bundle"

    @api.onchange('template_id')
    def _clear_variants(self):
        for rec in self:
            rec.variants = []
    