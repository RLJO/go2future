# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
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
    '''Product model inherit product.product.'''

    _inherit = 'product.product'

    image_128_parse = fields.Char(compute='_parse_image_128')

    @api.depends('image_128')
    def _parse_image_128(self):
        '''Computed fields return image as string.'''
        self.image_128_parse = self.image_128.decode('ascii')

    def get_product_by_code(self, code=''):
        '''get product by code pased.'''

        domain = [
            ('default_code', '=', code),
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True)
        ]

        response = self.parse_products(domain)
        return dumps(response)

    def parse_products(self, domain=None):
        '''Return products parse.'''

        products = self.env['product.product']
        response = products.search_read(domain,
                                        ['name',
                                         'alternative_product_ids',
                                         'categ_id',
                                         'code',
                                         'company_id',
                                         'default_code',
                                         'description',
                                         'description_purchase',
                                         'display_name',
                                         # 'image_128',
                                         'image_128_parse',
                                         # 'image_variant_128',
                                         'is_published',
                                         'list_price',
                                         'website_id',
                                         'sale_ok'])
        return response
