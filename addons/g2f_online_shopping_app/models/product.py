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

    def parse_products_online_shopping(self, domain=[]):
        """Return  products parse for online shopping."""

        search_products = self.search(domain)
        response = [{
            'name': p.name, 'product_description': p.product_description, 
            'categ_id_name': p.categ_id.name, 'brand': p.brand,
            'contents': p.contents, 'uom_id_name': p.uom_id.name, 
            'barcode': p.barcode, 'country_id_name': p.country_id.name, 
            'marketplace_seller_id': p.marketplace_seller_id.name, 
            'list_price': p.list_price, 'uom_price': p.uom_price, 
            'vegan': p.vegan, 'organic': p.organic, 
            'without_tacc': p.without_tacc, 'sugar_free': p.sugar_free, 
            'alternative_product_ids': [f.name for f in p.alternative_product_ids], 
            'public_categ_ids': [c.name for c in p.public_categ_ids], 
            'image_1920': p.image_1920.decode("ascii"), 
            'iframe': p.iframe} for p in search_products
            ]
        return response

    def parse_product_public_category(self, domain=[]):
        """Return parse product public category list."""

        ppcatg = self.env['product.public.category'].search(domain)
        response = [{
            'name': f.name,
            'padre': f.parent_id.name if f.parent_id else ''} 
            for f in ppcatg]

        print(response)

    def products_for_category_list(self, domain=[]):
        """Return list product for category."""

        ppcatg = self.env['product.public.category'].search(domain)
        response = [{
            'category_id': category.id,
            'category': category.name,
            'product_tmpl_ids': 
            [product.name for product in category.product_tmpl_ids]
            } 
            for category in ppcatg.filtered('product_tmpl_ids')]
        print(response)

