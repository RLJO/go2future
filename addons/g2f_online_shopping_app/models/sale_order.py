# pylint: disable=eval-used
# pylint: disable=broad-except
# -

from datetime import datetime
import logging
from odoo import models, fields, _
from odoo import http

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Sale order model by Api Mobile."""

    _inherit = 'sale.order'

    SHIPMENT = [
        ('P', 'Pickup'),
        ('D', 'Delivery')]

    shipment_type = fields.Selection(SHIPMENT, string='shipment type')
    shipment_datetime = fields.Datetime(string='shipment datetime')

    def sale_create(self, values):
        user = self.env['res.partner'].validate_user(values.get('user'))
        sale_order_type = self.env['sale.order.type'].search([('code', '=', values.get('sale_order_type'))])
        store_id = self.env['stock.warehouse'].search([('code', '=', values.get('store_id'))])
        vals = {
            "partner_id": user.partner_id.id,
            "warehouse_id": store_id.id,
            "sale_order_type": sale_order_type.id,
            "user_id": 2
        }
        sale_id = self.env['sale.order'].create(vals)
        lines = []
        for line in values.get('lines'):
            line_obj = self.env['sale.order.line']
            product = self.env['product.product'].search([('barcode', '=', line.get("product_id"),)])

            line_id = line_obj.create({
                "order_id": sale_id.id,
                "product_id": product.id,
                #'seller': product.seller_ids.name.id,
                "product_uom_qty": line.get("product_uom_qty")
            })
            line_id.product_id_change()
            lines.append(line_id.id)
        sale_id.action_confirm()

        data = {}
        _logger.info('order: {}'.format(sale_id.name))
        payments = [(t.bin, t.card_type, t.card_brand, t.status)
                    for t in sale_id.payment_prisma_attempt_ids]

        data = {"order": sale_id.name,
                "create_date": sale_id.create_date.strftime(
                    "%Y-%m-%d, %H:%M:%S"),
                "store": sale_id.user_id.name,
                "amount_total": sale_id.amount_total,
                "download_invoice": self._link_download_invoice(sale_id),
                "payments": payments
                }

        return data

