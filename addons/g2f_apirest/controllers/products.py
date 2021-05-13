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

    @http.route(['/products/get_product_details/<int:warehouse_id>'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def product_all(self, **kw):
        method = http.request.httprequest.method
        print(kw)
        warehouse_id = kw.get('warehouse_id')

        if method == 'GET':
            print('Listar, Obtener Productos')
            product_list = self.get_product_list(warehouse_id)
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

    def get_product_list(self, warehouse_id):
        """Get product list."""
        # Considerar filtrar por ultima fecha de actualizacion del Producto
        # Considerar devolver los campos que ellos necesiten

        products = http.request.env['product.product']
        domain = [
            ('active', '=', True),
            ('sale_ok', '=', True),
            ('is_published', '=', True),
            ('warehoue_id', '=', warehouse_id)]
        response = {"status": 200, "data": []}

        response["data"] = products.sudo().parse_products(domain)
        return dumps(response['data'])

    @http.route(['/update_gondola'], type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_gondola(self):
        return 'Ejecutar aqui un post a la API de los indios'
