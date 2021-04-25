# pylint: disable=broad-except

from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class Product(http.Controller):
    @http.route(['/products'], type='http', auth='public',
                methods=['POST', 'PUT', 'DELETE', 'GET'],
                website=True, csrf=False)
    def product(self, **kw):
        method = http.request.httprequest.method
        print(kw)

        if method == 'GET':
            print('Entro en Get')
            x = self.get_product(kw)
            return x

        if method == 'POST':
            print('Aun no se')
            return 'Metodo Post'

        if method == 'PUT':
            print('Modificar Producto')

        if method == 'DELETE':
            print('Eliminar Productos')
        return False

    @http.route(['/products/GetAll'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def productAll(self, **kw):
        method = http.request.httprequest.method
        print(kw)

        if method == 'GET':
            print('Listar, Obtener Productos')
            product_list = self.get_product_list()
            print(product_list)
            return product_list

    def get_product(self, kw):
        default_code = kw.get('default_code')
        domain = [
            ('default_code', '=', default_code),
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True)]

        response = {"status": 200, "data": []}
        response["data"] = self.parse_products(domain)

        return dumps(response)

    def get_product_list(self):
        # Considerar filtrar por ultima fecha de actualizacion del Producto
        # Considerar devolver los campos que ellos necesiten

        domain = [
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True)]

        response = {"status": 200, "data": []}
        response["data"] = self.parse_products(domain)

        for product in response['data']:
            if product.get('image_128'):
                product['image_128'] = product.get('image_128').decode('ascii')

        return dumps(response['data'])

    def parse_products(self, domain=[]):
        products = http.request.env['product.product']
        response = products.sudo().search_read(domain,
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
        return response

    @http.route(['/update_gondola'], type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_gondola(self):
        return 'Ejecutar aqui un post a la API de los indios'
