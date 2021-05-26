# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_children = fields.Boolean(string=_('Has children'), default=False)
    children_parent_id = fields.Many2one('res.partner', string=_("Marketplace Parent"))
    res_partner_children = fields.One2many('res.partner', 'children_parent_id')
    warehouse_ids = fields.Many2many('stock.warehouse', 'res_partner_stock_warehouse_rel', 'partner_id', 'warehouse_id',
                                     string=_('Warehouse'))
    warehouse_ids_domain = fields.Many2many('stock.warehouse', compute='_compute_warehouse_ids_domain', readonly=False,
                                            store=False)
    journal_id = fields.Many2one('account.journal', string=_('Bank'), domain='[("type", "=", "bank")]')
    bank_id = fields.Many2one('res.bank', string='Bank')
    acc_number = fields.Char('Account Number')

    def update_warehouse_ids_domain(self, partner):
        warehouse_ids = []
        warehouse_ids += [warehouse.ids[0] for warehouse in partner.warehouse_ids]
        childrens = self.search([('children_parent_id', 'in', partner.ids)])
        for children in childrens:
            pass
            warehouse_ids += [warehouse.id for warehouse in children.warehouse_ids]
        warehouse_ids = list(dict.fromkeys(warehouse_ids))
        return warehouse_ids

    @api.depends('children_parent_id', 'warehouse_ids')
    def _compute_warehouse_ids_domain(self):
        used_ids = []
        for record in self:
            if not record.ids:
                continue
            parent = record
            if parent.children_parent_id:
                parent = self.sudo().browse(parent.ids[0]).children_parent_id
            used_ids += record.update_warehouse_ids_domain(parent)
            record.warehouse_ids_domain = [(6, 0, used_ids)]

    @api.onchange('warehouse_ids_domain')
    def _onchange_warehouse_ids_domain(self):
        domain = {
            'domain': {
                'warehouse_ids': [('id', 'not in', self.warehouse_ids_domain.ids)]
            }
        }
        if not domain:
            domain = False
        return domain

    def approve(self):
        self.ensure_one()
        if self.seller:
            user = self.env['res.users'].sudo().search([('partner_id', '=', self.id)])
            if len(user) > 1:
                user = user[0]
            user.write({
                'groups_id': [
                    (4, self.env.ref('odoo_marketplace_custom.group_marketplace_children_create').id),
                    (4, self.env.ref('base.group_partner_manager').id)
                ]
            })
        super(ResPartner, self).approve()

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res:
            self.update_product_seller(res)
            if not 'type' in vals:
                if res.write_uid.partner_id.seller:
                    res.children_parent_id = res.write_uid.partner_id.id
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if res:
            self.update_product_seller(self)
        return res

    def update_seller(self):
        self.update_product_seller(self)

    def update_product_seller(self, partner):

        product_template_env = self.env['product.template'].sudo()
        product_product_env = self.env['product.product'].sudo()
        product_supplierinfo = self.env['product.supplierinfo'].sudo()
        stock_quant_env = self.env['stock.quant'].sudo()
        stock_warehouse_env = self.env['stock.warehouse'].sudo()
        product_owner_warehouse = {}

        product_template = product_template_env.search([('marketplace_seller_id', '=', partner.id)])
        for template_item in product_template:
            products = product_product_env.search([('product_tmpl_id', '=', template_item.id)])
            for product in products:
                stock_records = stock_quant_env.search([('product_id', '=', product.id)])
                for stock_item in stock_records:
                    product_owner_warehouse = {}
                    warehouse = stock_warehouse_env.search([('lot_stock_id', '=', stock_item.location_id.id), ('active', '=', True)])
                    if warehouse:
                        if not str(template_item.id) + '-' + str(warehouse.id) in product_owner_warehouse:
                            product_owner_warehouse.update({
                                'warehouse_id': warehouse.id,
                                'product_id': template_item.id,
                                'partner_id': partner.id,
                            })

                            if partner.has_children and partner.res_partner_children:
                                for children in partner.res_partner_children:
                                    for children_warehouse in children.warehouse_ids:
                                        if children_warehouse.id == warehouse.id:
                                            product_owner_warehouse['partner_id'] = children.id

                            partner_warehouse = product_supplierinfo.search([('product_tmpl_id', '=', product_owner_warehouse['product_id']), ('name', '=', product_owner_warehouse['partner_id']), ('warehouse_id', '=', product_owner_warehouse['warehouse_id'])])
                            if not partner_warehouse:
                                product_supplierinfo.create({
                                    'name': product_owner_warehouse['partner_id'],
                                    'warehouse_id': product_owner_warehouse['warehouse_id'],
                                    'product_tmpl_id': product_owner_warehouse['product_id']
                                })
                            else:
                                for item in partner_warehouse:
                                    item.write({
                                        'name': product_owner_warehouse['partner_id'],
                                        'warehouse_id': product_owner_warehouse['warehouse_id'],
                                    })

    def change_seller_group(self, set_to_group=None):
        """ param: set_to_group should be string, value must be 'not_seller' or 'seller' only. """

        if not set_to_group:
            return
        login_user_obj = self.env.user
        if not login_user_obj.has_group('odoo_marketplace.marketplace_officer_group'):
            _logger.info(_("~~~~~~~~~~You are not an autorized user to change seller account access. Please contact your administrator. "))
            raise UserError(_("You are not an autorized user to change seller account access. Please contact your administrator. "))
        for seller in self.filtered(lambda o: o.seller == True):
            seller_user = self.env["res.users"].sudo().search([('partner_id', '=', seller.id)])
            pending_seller_group_obj = self.env.ref('odoo_marketplace.marketplace_draft_seller_group')
            seller_group_obj = self.env.ref('odoo_marketplace.marketplace_seller_group')
            if set_to_group == "seller":
                #First check seller user realy belongs to draft seller group(marketplace_draft_seller_group) or not
                if seller_user.has_group("odoo_marketplace.marketplace_draft_seller_group"):
                    # Remove seller user from draft seller group(marketplace_draft_seller_group)
                    pending_seller_group_obj.sudo().write({"users": [(3, seller_user.id, 0)]})
                    # Add seller user to seller group(marketplace_seller_group)
                    seller_group_obj.sudo().write({"users": [(4, seller_user.id, 0)]})
                else:
                    _logger.info(_("~~~~~~~~~~Seller does not belongs to draft seller group. So you can't change seller group to seller group."))
            elif set_to_group == "not_seller":
                #First check seller user realy belongs to seller group(marketplace_seller_group) or not
                if seller_user:
                    if seller_user.has_group("odoo_marketplace.marketplace_seller_group"):
                        # Remove seller user from seller group(marketplace_seller_group)
                        seller_group_obj.write({"users": [(3, seller_user.id, 0)]})
                        # Add seller user to draft seller group(marketplace_draft_seller_group)
                        pending_seller_group_obj.write({"users": [(4, seller_user.id, 0)]})
