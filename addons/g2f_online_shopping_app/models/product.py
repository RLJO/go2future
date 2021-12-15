# pylint: disable=eval-used
# pylint: disable=broad-except
# -

from json import dumps
import logging
from odoo import models, fields, api, _

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """Product model inherit product.product."""

    _inherit = 'product.product'

    def parse_products(self, domain=None):
        """Return  products parse."""

        values = super(ProductProduct, self).parse_products(domain)

        response = self.search_read(
                domain,[
                    'name', 'product_description', 'categ_id', 'brand',
                    'contents', 'uom_id', 'barcode', 'country_id', 
                    'marketplace_seller_id', 'list_price', 'uom_price', 
                    'vegan', 'organic', 'without_tacc', 'sugar_free', 
                    'alternative_product_ids',
                    ] 
                )
        return response

