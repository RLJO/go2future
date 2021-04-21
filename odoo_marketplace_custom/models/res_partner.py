# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_children = fields.Boolean(string=_('Has children'), default=False)
    children_parent_id = fields.Many2one('res.partner', string=_("Marketplace Parent"))
    res_partner_children = fields.One2many('res.partner', 'children_parent_id')
    warehouse_ids = fields.Many2many('stock.warehouse', 'res_partner_stock_warehouse_rel', 'partner_id', 'warehouse_id', string=_('Warehouse'))
    journal_id = fields.Many2one('account.journal', string=_('Bank'), domain='[("type", "=", "bank")]')

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
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if res:
            self.update_product_seller(self)
        return res

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

