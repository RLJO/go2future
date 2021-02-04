# pylint: disable=broad-except

from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class Product(http.Controller):
    @http.route(['/products'], type='http', auth='public',
                methods=['GET', 'POST', 'PUT', 'DELETE'],
                website=True, csrf=False)
    def product(self, **kw):
        method = http.request.httprequest.method
        print(kw)

        if method == 'POST':
            print('Aun no se')
            return 'Metodo Post'

        if method == 'PUT':
            print('Modificar Producto')

        if method == 'GET':
            print('Listar, Obtener Productos')
            product_list = self.get_product_list()
            print(product_list)
            return product_list

        if method == 'DELETE':
            print('Eliminar Productos')
        return False

    def get_product_list(self):
        # Considerar filtrar por ultima fecha de actualizacion del Producto
        # Considerar devolver los campos que ellos necesiten

        products = http.request.env['product.product'].sudo().search([
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True)])
        
        response = products.search_read([],
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
                                         # 'image_variant_128',
                                         'is_published',
                                         'list_price',
                                         'website_id',
                                         'sale_ok'])
        """
        for product in response:
            if product.get('image_128'):
                product.update('image_128',
                               product.get('image_128').decode('ascii'))
                               """

        return dumps(response)

    @http.route(['/update_gondola'], type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_gondola(self):
        return 'Ejecutar aqui un post a la API de los indios'

    """
    name
    alternative_product_ids
    categ_id
    code
    company_id
    default_code(referencia interna)
    description
    description_purchase
    display_name
    image_128
    image_256
    image_512
    image_1024
    image_1920
    image_variant_128
    image_variant_256
    image_variant_512
    image_variant_1024
    image_variant_1920
    is_published
    list_price(Precio de venta)
    website_id
    sale_ok"""
