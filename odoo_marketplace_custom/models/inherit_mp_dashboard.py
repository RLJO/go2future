# -*- coding: utf-8 -*-

from odoo import models, fields, _
import logging
_logger = logging.getLogger(__name__)


class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_partner_children(self):
        login_user_obj = self.env.user
        for rec in self:
            domain = [('children_parent_id', '=', rec.env.user.partner_id.id)]
            if login_user_obj.has_group('odoo_marketplace.marketplace_manager_group'):
                domain = [('children_parent_id', '!=', False)]
            obj_children = self.env['res.partner'].sudo().search(domain)
            if obj_children:
                rec.count_partner_children = len(obj_children)
            else:
                rec.count_partner_children = 0

    def action_res_partner_children(self):
        login_user_obj = self.env.user
        domain = ('children_parent_id.id', '=', self.env.user.partner_id.id)
        if login_user_obj.has_group('odoo_marketplace.marketplace_manager_group'):
            domain = ('children_parent_id', '!=', False)
        return {
            'name': _('Children'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'views': [
                [self.env.ref('odoo_marketplace_custom.res_partner_children_kanban').id, 'kanban'],
                [self.env.ref('odoo_marketplace_custom.res_partner_children_tree').id, 'tree'],
                [self.env.ref('odoo_marketplace_custom.res_partner_children_form').id, 'form']
            ],
            'domain': [
                domain
            ]
        }

    def action_marketplace_vendor_percentage(self):
        login_user_obj = self.env.user
        domain = ('partner_id.id', '=', self.env.user.partner_id.id)
        if login_user_obj.has_group('odoo_marketplace.marketplace_manager_group'):
            domain = ('partner_id', '!=', False)
        return {
            'name': _('Marketplace Vendedor %'),
            'type': 'ir.actions.act_window',
            'res_model': 'marketplace.vendor',
            'view_mode': 'tree',
            'domain': [
                domain
            ]
        }

    state = fields.Selection(
        [('product', 'Product'), ('seller', 'Seller'), ('order', 'Order'), ('payment', 'Payment'), ('children', 'Children')])
    count_partner_children = fields.Integer(compute='_get_partner_children')
