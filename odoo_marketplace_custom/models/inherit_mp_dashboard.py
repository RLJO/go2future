# -*- coding: utf-8 -*-

from odoo import models, fields, _
import logging
_logger = logging.getLogger(__name__)


class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_partner_children(self):
        for rec in self:
            obj_children = self.env['res.partner'].sudo().search(
                [('children_parent_id', '=', rec.env.user.partner_id.id)])
            if obj_children:
                rec.count_partner_children = len(obj_children)
            else:
                rec.count_partner_children = 0

    def action_res_partner_children(self):
        return {
            'name': _('Children'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'res_model': 'res.partner',
            'view_id': self.env.ref('odoo_marketplace_custom.res_partner_children_kanban').id,
            'domain': [
                ('children_parent_id.id', '=', self.env.user.partner_id.id)
            ]
        }

    state = fields.Selection(
        [('product', 'Product'), ('seller', 'Seller'), ('order', 'Order'), ('payment', 'Payment'), ('children', 'Children')])
    count_partner_children = fields.Integer(compute='_get_partner_children')
