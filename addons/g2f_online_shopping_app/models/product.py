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


    class ProductPublicCategory(models.Model):
        """Product Public Category model inherit ."""

        _inherit = 'product.public.category'

        def product_public_category_list(self, domain=[]):
            """Return Public Category List,
               By Default domain = [] ."""


            parent_ids = [{"id": c.id, "name":c.name} 
                    for c in self.search(domain) if c.parent_id.id<=0]

            lista = []
            for parent_id in parent_ids:
                child_ids = self.search(
                        [('parent_id', '=', parent_id.get('id'))])
                childs_of = [{"id": child.id, "name":child.name} 
                        for child in child_ids]
                line = {"id":parent_id.get('id'), 
                        "name": parent_id.get("name"), 
                        "childs": childs_of}
                lista.append(line)
            return lista
