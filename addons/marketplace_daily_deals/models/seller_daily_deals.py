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

from odoo import models,fields,api,_
import logging
_logger = logging.getLogger(__name__)

class WebsiteDeals(models.Model):
    _inherit = 'website.deals'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", default=_set_seller_id, copy=False)

    def update_cron(self):
        return super(WebsiteDeals,self.sudo()).update_cron()


class product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    logged_in_user_group_ids = fields.Many2many('res.partner',compute='_compute_user_group_ids')

    @api.depends('website_deals_m2o.marketplace_seller_id')
    def _compute_user_group_ids(self):
        for rec in self:
            login_ids = []
            seller_group = rec.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_seller_group')[1]
            officer_group = rec.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_officer_group')[1]
            groups_ids = rec.env.user.sudo().groups_id.ids
            if seller_group in groups_ids and officer_group not in groups_ids:
                login_ids.append(rec.env.user.sudo().partner_id.id)
                marketplace_seller_id = rec.env.user.sudo().partner_id.id
            elif seller_group in groups_ids and officer_group in groups_ids:
                seller_id = rec.website_deals_m2o.marketplace_seller_id
                if seller_id:
                    login_ids.append( seller_id.id)
            rec.logged_in_user_group_ids = [(6,0,login_ids)]

