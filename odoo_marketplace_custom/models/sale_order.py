# -*- coding: utf-8 -*-

from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    marketplace_vendor_line = fields.One2many('marketplace.vendor', 'sale_order')
    amount_marketplace_vendor = fields.Float(compute='_compute_amount_marketplace_vendor', string=_('Amount vendor'))
    amount_marketplace = fields.Float(compute='_compute_amount_marketplace', string=_('Amount marketplace'))

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.create_marketplace_vendor()
        return result

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self.create_marketplace_vendor()
        return res

    def create_marketplace_vendor(self):
        for marketplace_vendor in self.marketplace_vendor_line:
            marketplace_vendor.unlink()
        for line in self.order_line:
            vals = {
                'sale_order': self.id,
                'name': line.seller.id,
                'amount_sale': line.price_subtotal,
                'sale_percentage': line.seller.commission,
                'sale_order_line': line.id,
                'product_id': line.product_id.id
            }
            self.marketplace_vendor_line.sudo().create(vals)

    def _compute_amount_marketplace_vendor(self):
        if self:
            amount_sale_percentage = 0.0
            for marketplace_vendor in self.marketplace_vendor_line:
                amount_sale_percentage += marketplace_vendor.amount_sale_percentage
            self.amount_marketplace_vendor = amount_sale_percentage
        else:
            self.amount_marketplace_vendor = 0.0

    def _compute_amount_marketplace(self):
        self.amount_marketplace = self.amount_total - self.amount_marketplace_vendor

    def _invoice_lines_by_seller(self, order_lines):
        seller_lines = []
        lines = []
        down_payment_line = []
        sellers = {}
        position = 0
        for line in order_lines:
            if line.display_type in ['line_section', 'line_note']:
                down_payment_line.append(line.id)
            else:
                if str(line.seller.id) not in sellers:
                    sellers[str(line.seller.id)] = position
                    lines.append([line.id])
                    position += 1
                else:
                    lines[sellers[str(line.seller.id)]].append(line.id)

        for partner_line in lines:
            seller_lines.append(self.env['sale.order.line'].browse(partner_line + down_payment_line))
        return seller_lines

    def _get_invoice_grouping_keys(self):
        return ['company_id', 'seller_id', 'currency_id']

    def _create_invoices(self, grouped=False, final=False, date=None):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            invoice_values = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                raise self._nothing_to_invoice_error()

            seller_lines = self._invoice_lines_by_seller(invoiceable_lines)

            for seller_line in seller_lines:
                invoice_vals = invoice_values.copy()
                invoice_line_vals = []
                down_payment_section_added = False
                seller_id = 0
                for line in seller_line:
                    if not down_payment_section_added and line.is_downpayment:
                        # Create a dedicated section for the down payments
                        # (put at the end of the invoiceable_lines)
                        invoice_line_vals.append(
                            (0, 0, order._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence,
                            )),
                        )
                        dp_section = True
                        invoice_item_sequence += 1
                    invoice_line_vals.append(
                        (0, 0, line._prepare_invoice_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    invoice_item_sequence += 1
                    seller_id = line.seller.id

                invoice_vals['seller_id'] = seller_id
                invoice_vals['warehouse_id'] = order.warehouse_id.id
                invoice_vals['invoice_line_ids'] = invoice_line_vals
                invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves_ids = []
        for invoice_vals in invoice_vals_list:
            moves_ids.append(self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create([invoice_vals]).id)
        moves = self.env['account.move'].sudo().browse(moves_ids)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    seller = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade',
        help="Vendor of this product")

    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(SaleOrderLine, self).product_id_change()
        if not self.order_id.warehouse_id:
            raise UserError(
                _('Debe seleccionar el almacén correspondiente'))
        if self.product_id:
            if self.product_id.seller_ids:
                seller_line = self.product_id.seller_ids
                seller_ids = seller_line.filtered(
                    lambda seller_line: seller_line.warehouse_id == self.order_id.warehouse_id)
                if len(seller_ids) == 1:
                    self.seller = seller_ids.name.id
                else:
                    if len(seller_ids) > 1:
                        self.seller = seller_ids[0].name.id
                    else:
                        raise UserError(
                            _('Producto no Posee Vendedor asignado para el almacen solicitado %s',
                              self.order_id.warehouse_id.name))
            else:
                raise UserError(
                    _('Producto no Posee Vendedor asignado'))
        return domain

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values['warehouse_id'] = self.order_id.warehouse_id
        return values


class MarketplaceVendor(models.Model):
    _name = "marketplace.vendor"

    sale_order = fields.Many2one('sale.order')
    sale_order_line = fields.Many2one('sale.order.line')
    name = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade',
        help=_("Vendor of this product"))
    product_id = fields.Many2one('product.template', 'Template')
    sale_percentage = fields.Float(related='name.commission', string=_('%'))
    amount_sale = fields.Float(string=_("Amount"))
    amount_sale_percentage = fields.Float(compute="_compute_amount_sale_percentage", string=_('Amount %'))
    product_id = fields.Many2one('product.product', string=_('Product'))

    def _compute_amount_sale_percentage(self):
        if self:
            for marketplace_vendor in self:
                percentage = (marketplace_vendor.sale_percentage / 100)
                marketplace_vendor.amount_sale_percentage = marketplace_vendor.amount_sale * percentage

class AccountMove(models.Model):
    _inherit = 'account.move'

    warehouse_id = fields.Many2one('stock.warehouse', string=_("Warehouse"))
    seller_id = fields.Many2one('res.partner', string=_('Seller'))
