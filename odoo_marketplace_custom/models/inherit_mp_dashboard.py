# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_partner_children(self):
        login_user_obj = self.env.user
        for rec in self:
            domain = ['|', ('children_parent_id', '=', rec.env.user.partner_id.id),
                      ('other_parent_ids', 'in', rec.env.user.partner_id.id)]
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
        domain = [('name.id', '=', self.env.user.partner_id.id)]
        if login_user_obj.has_group('odoo_marketplace.marketplace_manager_group'):
            domain = [('partner_id', '!=', False)]
        return {
            'name': _('Marketplace Vendedor %'),
            'type': 'ir.actions.act_window',
            'res_model': 'marketplace.vendor',
            'view_mode': 'tree',
            'domain': domain,
            'context': {
                'search_default_date': True,
                'search_default_name': 1,
            },
        }

    def _get_approved_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '=', ids), ('status', '=', 'approved')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'approved')])
                rec.count_product_approved = len(obj)
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'approved')])
                rec.count_product_approved = len(obj)
            elif rec.state == 'order':
                if rec.is_seller:
                    user_obj = self.env['res.users'].browse(rec._uid)
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', ids), ('marketplace_state', '=', 'approved'),('state', 'not in', ('draft', 'sent'))])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('marketplace_state', '=', 'approved'),('state', 'not in', ('draft', 'sent'))])
                rec.count_product_approved = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'posted')])
                rec.count_product_approved = len(obj)
            else:
                rec.count_product_approved = 0

    def _get_pending_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '=', ids), ('status', '=', 'pending')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'pending')])
                rec.count_product_pending = len(obj)
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'pending')])
                rec.count_product_pending = len(obj)
            elif rec.state == 'order':
                #user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', ids), ('marketplace_state', '=', 'new'),('state', 'not in', ('draft', 'sent'))])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('marketplace_state', '=', 'new'),('state', 'not in', ('draft', 'sent'))])
                rec.count_product_pending = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'requested')])
                rec.count_product_pending = len(obj)
            else:
                rec.count_product_pending = 0

    def _get_rejected_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '=', ids), ('status', '=', 'rejected')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'rejected')])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'denied')])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'order':
                #user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    user = self.env.user
                    ids = [user.partner_id.id]
                    if user.partner_id.children_parent_id:  # Padre
                        ids.append(user.partner_id.children_parent_id.id)
                    if user.other_parent_ids:  # otros padres
                        ids += user.other_parent_ids.ids
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', ids), ('marketplace_state', '=', 'shipped'),('state', 'not in', ('draft', 'sent'))])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('marketplace_state', '=', 'shipped'),('state', 'not in', ('draft', 'sent'))])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'confirm'), ('payment_mode', '=', 'seller_payment')])
                rec.count_product_rejected = len(obj)
            else:
                rec.count_product_rejected = 0

    state = fields.Selection(
        [('product', 'Product'), ('seller', 'Seller'), ('order', 'Order'), ('payment', 'Payment'), ('children', 'Children')])
    count_partner_children = fields.Integer(compute='_get_partner_children')
    sequence = fields.Integer('Sequencia')

    @api.model
    def update_data(self):
        products = self.sudo().browse(self.env.ref('odoo_marketplace.product_demo').id)
        products.write({
            'name': 'Productos MiniGo',
            'sequence': 1,
        })
        sellers = self.sudo().browse(self.env.ref('odoo_marketplace.seller_demo').id)
        sellers.write({
            'name': 'Vendedores',
            'sequence': 2,
        })
        childrens = self.sudo().browse(self.env.ref('odoo_marketplace_custom.children_marketplace').id)
        childrens.write({
            'name': 'Vendedores Hijos MiniGO',
            'sequence': 3,
        })
        payments = self.sudo().browse(self.env.ref('odoo_marketplace.payment_demo').id)
        payments.write({
            'name': 'Detalle ventas y comisiones',
            'sequence': 4,
        })
