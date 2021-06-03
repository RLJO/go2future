#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            if record.active:
                packs = self.env['product.template'].search(
                    [('is_bundle', '=', True)])
                for pack in packs:
                    for line in pack.wk_bundle_products:
                        if record.id == line.template_id.id:
                            raise UserError(
                                'You can not archive this product because it is present in the pack %s. For archiving this product you need to remove it from the pack.' % pack.name)
        return super(ProductTemplate, self).toggle_active()

    def compute_discounted_bundle_price(self):
        for product in self:
            if product.is_bundle:
                price = 0
                for prod in product.wk_bundle_products:
                    price = price + prod.template_id.lst_price * prod.product_quantity
                rem_price = price - product.lst_price
                product.bundle_products_price = price
                if rem_price <= 0:
                    product.show_web_label = True
                else:
                    product.show_web_label = False

            else:
                product.show_web_label = False
                product.bundle_products_price = 0.00

    is_bundle = fields.Boolean(
        string='Is Bundle')
    wk_bundle_products = fields.One2many(
        comodel_name='product.bundle',
        inverse_name='wk_product_template',
        string='Bundle Products')
    pack_stock_management = fields.Selection(
        [('decrmnt_pack', 'Decrement Pack Only'),
         ('decrmnt_products', 'Decrement Products'),
         ('decrmnt_both', 'Decrement Both')],
        string='Pack Stock Management',
        default='decrmnt_both',
        help="this field actually changes the type of pack to consumable , service and stockable respectively")
    show_web_label = fields.Boolean(
        compute="compute_discounted_bundle_price",
        string="Remaning price")
    bundle_products_price = fields.Float(
        compute="compute_discounted_bundle_price",
        string="Total Product Price")
    bundle_type = fields.Selection(
        [('fixed_quantity', 'Fixed Quantity'),
         ('variable_quantity', 'Variable Quantity')],
        string="Bundle Type",
        default="fixed_quantity",
        help="Type of the bundle, ether fix the quantity in bundle or allow the users to add the quantity."
    )

    @api.model
    def get_actual_product_price(self, product_id):
        if product_id:
            template_id = self.sudo().browse(product_id)
            if template_id.is_bundle:
                price = 0
                for temp_line in template_id.wk_bundle_products:
                    price = price + temp_line.template_id.list_price * temp_line.product_quantity
                return price - template_id.lst_price

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            prd_type = 'service'
        elif pk_dec == 'decrmnt_both':
            prd_type = 'product'
        else:
            prd_type = 'consu'
        self.type = prd_type

    @api.onchange('bundle_type')
    def onchange_bundle_type(self):
        """
        Do not allow to change the bundle type if the products are already set.
        """
        if self.wk_bundle_products:
            raise UserError(
                'You can not change the Bundle Type once the products are added in the bundle.')

    @api.model
    def show_amount_saved_in_shop_page(self):
        return self.env['ir.default'].sudo().get('dynamic.bundle.products.config', 'amount_saved_shop_page')

    @api.model
    def show_amount_saved_in_product_page(self):
        return self.env['ir.default'].sudo().get('dynamic.bundle.products.config', 'amount_saved_in_product_page')

    @api.model
    def create(self, vals):
        if vals.get('is_bundle'):
            if not vals.get('wk_bundle_products'):
                raise UserError(
                    'You can not create a pack without products!!!')
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if vals.get('is_bundle'):
            if vals.get('wk_bundle_products') and not vals.get('wk_bundle_products')[0][2]:
                raise UserError(
                    'You can not create a pack without products!!!')
        if not vals.get('is_bundle'):
            return super(ProductTemplate, self).write(vals)
        return super(ProductTemplate, self).write(vals)


class ProductPack(models.Model):
    _name = 'product.bundle'
    _description = "Product Bundle"

    template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        required=True,
        domain=[('is_bundle', '=', False)])
    wk_product_template = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True)
    # this is key to product template ....
    product_quantity = fields.Integer(
        string='Quantity in Bundle',
        default=1)
    price = fields.Float(
        related='template_id.list_price',
        string='Product Price')
    name = fields.Char(
        related='template_id.name',
        readonly="1")
    add_variants = fields.Selection(
        [('all', 'All'),
         ('selected', 'Selected')],
        string='Variants To Show In Bundle',
        default='all', required=True,
        help="These variants will be available to the customer while choosing a pack, and he can select the products from these variants.")
    variants = fields.Many2many(
        'product.product',
        'pack_product_rel',
        'product_pack',
        'product_id',
        string='Variants')
    bundle_type = fields.Selection(
        [('fixed_quantity', 'Fixed Quantity'),
         ('variable_quantity', 'Variable Quantity')],
        string="Bundle Type",
        help="Type of the bundle, either fix the quantity in bundle or allow the users to modify the quantity.",
    )
    min_bundle_qty = fields.Integer(
        string='Min Quantity In Bundle',
        default=0,
        help="Minimum Quantity customer must buy. Zero represents no minimum quantity.")
    max_bundle_qty = fields.Integer(
        string='Max Quantity In Bundle',
        default=0,
        help="Maximum Quantity customer can buy. Zero represents no maximum quantity.")

    @api.model
    def create(self, vals):
        if vals.get('template_id') and vals.get('add_variants') == 'all':
            temp_obj = self.env['product.template'].browse(
                vals.get('template_id'))
            vals['variants'] = [(6, 0, temp_obj.product_variant_ids.ids)]
        return super(ProductPack, self).create(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_bundle = fields.Many2one(
        comodel_name='product.bundle', string='Product Pack')

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            self.type = 'service'
        elif pk_dec == 'decrmnt_both':
            self.type = 'product'
        else:
            self.type = 'consu'
        return {'value': self.type}
		
    @api.model
    def get_variant_attributes(self):
        AttString = []
        for attr in self:
            _name = attr._get_combination_info_variant()
            AttString.append(_name.get('display_name',''))
        AttString = ",".join(str(x) for x in AttString)
        return AttString


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    wk_product_variants = fields.One2many(
        comodel_name='created.dynamic.pack', inverse_name='order_line_id', string='Pack Product Variants')

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        for line in self:
            procurements = []
            errors = []
            if line.product_id.is_bundle:
                qty = 0.0
                for move in line.move_ids:
                    qty += move.product_qty
                if not line.order_id.procurement_group_id:
                    line.order_id.procurement_group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name,
                        'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                values = line._prepare_procurement_values(
                    group_id=line.order_id.procurement_group_id)

                if line.product_id.pack_stock_management == 'decrmnt_both':
                    product_qty = line.product_uom_qty - qty

                    try:
                        procurements.append(self.env['procurement.group'].Procurement(
                            line.product_id, product_qty,  line.product_uom,
                            line.order_id.partner_shipping_id.property_stock_customer,
                            line.name, line.order_id.name, line.order_id.company_id, values))
                        if procurements:
                            self.env['procurement.group'].run(procurements)
                    except UserError as error:
                        errors.append(error.name)

                if line.product_id.pack_stock_management != 'decrmnt_pack':
                    for pack_obj in line.wk_product_variants:
                        procurements = []
                        product_qty = line.product_uom_qty * pack_obj.quantity_in_pack
                        try:
                            procurements.append(self.env['procurement.group'].Procurement(
                                pack_obj.variant_id, product_qty, line.product_uom,
                                line.order_id.partner_shipping_id.property_stock_customer,
                                line.name, line.order_id.name, line.order_id.company_id, values))
                            if procurements:
                                self.env['procurement.group'].run(procurements)
                        except UserError as error:
                            errors.append(error.name)
        return super(SaleOrderLine, self)._action_launch_stock_rule()


class CreatedDynamicPack(models.Model):
    _name = "created.dynamic.pack"
    _description = "Created Dynamic packs"
    order_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Order Line')
    variant_id = fields.Many2one(
        comodel_name='product.product', string='Product Varinat')
    quantity_in_pack = fields.Integer('Qunatity in Pack')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        order_line_obj = self.env['sale.order.line'].sudo().browse(line_id)
        product_obj = self.env['product.product'].sudo().browse(product_id)
        update_name = order_line_obj.name
        response = super(SaleOrder,self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        try:
            if product_obj.product_tmpl_id and product_obj.product_tmpl_id.is_bundle:
                order_line_obj.name = update_name
        except Exception:
            return response

        return response
