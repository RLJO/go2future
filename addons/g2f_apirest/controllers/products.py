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

    @http.route(['/products/get_product_details/'], type='json', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def product_all(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        print(kw)
        store_code = kw.get('store_code')

        if method == 'GET':
            print('Listar, Obtener Productos')
            product_list = self.get_product_list(store_code)
            print(product_list)
            return product_list

    def get_product(self, kw):
        default_code = kw.get('default_code')
        products = http.request.env['product.product']
        domain = [
            ('default_code', '=', default_code),
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True)]

        response = {"status": 200, "data": []}
        response["data"] = products.sudo().parse_products(domain)

        return dumps(response)

    def get_product_list(self, location_code):
        """Get product list."""

        response = {"status": 200, "data": []}

        products = http.request.env['product.product']
        get_products = products.sudo().search_product_by_location_code(location_code)
        product_list_id = [p.id for p in get_products]
        domain = [('id', 'in', product_list_id)]
        response["data"] = products.sudo().search_read(domain, ['id', 'name', 'weight'])
        return dumps(response['data'])

    @http.route(['/weight_sensor_data/'], type='http', auth='public',
             methods=['GET'], website=True, csrf=False)
    def get_weigth_sensor_data(self, **kw):
        method = http.request.httprequest.method
        print(kw)

        product = http.request.env['product.product']
        weight_sensor_id = kw.get('weight_sensor_id')
        response = {"status": 200, "data": []}

        if method == 'GET':
            print('Obtener Productos que estan ubicados dentro de un determinado sensor en una tienda')
            product_list = product.sudo().search_products_by_weight_sensor_id(weight_sensor_id)
            response["data"] = [{f'{p.id}': p.qty_available} for p in product_list]

            return dumps(response)

    @http.route(['/update_gondola'], type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_gondola(self):
        return 'Ejecutar aqui un post a la API de los indios'
