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
    """Product model inherit product.product."""

    _inherit = 'product.product'

    image_128_parse = fields.Char(compute='_parse_image_128')

    @api.depends('image_128')
    def _parse_image_128(self):
        """Computed fields return image as string."""
        self.image_128_parse = self.image_128.decode('ascii')

    def get_product_by_code(self, barcode=''):
        """get product by barcode pased."""

        domain = [
            ('barcode', '=', barcode),
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('status', '=', 'approved')
        ]

        response = self.parse_products(domain)
        return dumps(response)

    def parse_products(self, domain=None):
        """Return  products parse."""

        response = self.search_read(
                domain, 
                ['name', 'alternative_product_ids', 'categ_id', 'code',
                    'company_id', 'default_code', 'description', 'weight',
                    'description_purchase', 'display_name', 'image_128_parse',
                    'is_published', 'list_price', 'website_id', 'sale_ok']
                )
        return response

    def search_product_by_location_code(self, location_code):
        """Buscar productos ubicados en un determinada tienda pasada
        como parametro."""

        stock_location = self.env['stock.location'].search([('name', 'ilike', location_code)])
        lista_ubicaciones = [location.id for location in stock_location.child_ids]
        stock_quant_list = self.env['stock.quant'].search([('location_id', 'in', lista_ubicaciones)])
        product_ids = [stock.product_id.id for stock in stock_quant_list]

        product_list = self.search([('id', 'in', product_ids)])
        #print(product_list)
        return product_list

    def search_products_by_weight_sensor_id(self, sensor_id):
        """Permite buscar productos segun el senson de peso donde estan ubicados.

           Parameter: sensor_id
        """

        domain = [('name', '=', sensor_id)]
        store_sensor = self.env['store.sensor'].search(domain)
        if not store_sensor:
            return []
        stock_location_name = store_sensor.store_id.view_location_id.name
        print(stock_location_name)

        cab = []
        det = []
        productos = self.env['product.store'].search(
            [('store_id', '=', store_sensor.store_id.id),
             ('shelf_id', '=', store_sensor.id)]
        )
        for producto in productos:
            cab.append(f"{producto.product_id.barcode}")
            det.append({'qty': producto.qty_available_prod,
                        'unit_weight': producto.peso_bruto,
                        'weight_threshold': producto.weight_threshold,
                        'ia_model': producto.product_id.product_tmpl_id.ia_model.name
                        })

        response = dict(zip(cab, det))
        return response
