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

