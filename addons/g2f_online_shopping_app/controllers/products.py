# pylint: disable=broad-except

from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError

class Product(http.Controller):

    @http.route(['/online_shopping_app/products/get_product_details/'], 
            type='http', auth='public', methods=['GET'], website=True,
            csrf=False)
    def get_product(self, **kw):
        default_code = kw.get('default_code')
        products = http.request.env['product.product']
        domain = [
            ('default_code', '=', default_code),
            ('active', '=', True),
            ]

        response = {"status": 200, "data": []}
        response["data"] = products.sudo().parse_products(domain)

        """
        'name', 'product_description', 'categ_id.name', 'brand', 'contents',
        'uom_id.name', 'barcode', 'country_id', 'marketplace_seller_id.name',
        'list_price', '*uom_price', '*descuento', '*descuento_vigente_hasta',
        '*pecio al publico con descuento', '*link para visualizar img3D',
        'vegan', 'organic', 'without_tacc', 'sugar_free', 
        'alternative_product_ids', '*productos complementarios', 
        '* stock disponible del producto en la ubicacion para ventas'
        """

        return dumps(response)

"""
Nombre del producto.
Descripción.
Categoría.
Marca.
Contenido.
Unidad de medida.
EAN 13.
País de origen.
Vendedor.
Precio al publico.
Precio de cada unidad de referencia.
Descuento.
Descuento vigente hasta.
Precio al publico con descuento.
Link para visualizar imagen 3D del producto. (En Odoo se debe de crear un campo en los productos para copiar el iframe).
Atributos: vegano, orgánico, sin azúcar, sin tacc.
Productos alternativos o similares.
Productos complementarios.
Stock disponible del producto en la ubicación para ventas on line. (En Odoo se debe de crear un campo para configurar la ubicación para ventas on line por local)

"""
