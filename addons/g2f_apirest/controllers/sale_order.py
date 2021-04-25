# pylint: disable=broad-except

from datetime import datetime
import requests
from json import dumps
from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class SaleOrderCart(http.Controller):
    @http.route(['/user_cart'], type='json', auth='public',
            methods=['GET', 'PUT', 'POST', 'DELETE'], website=True, csrf=False)
    def sale_order_cart(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        user_id = kw.get('user')
        product_id = kw.get('product')
        action = kw.get('action')

        sale_order = http.request.env['sale.order']

        if method == 'GET':
            # Obtener lista de productos de orden de venta abierta
            
            response = sale_order.sudo()._get_sale_order_from_controller(
                    user_id)
            return dumps(response)

        elif method == 'POST':
            #  Agregar un prodcuto a una orden de venta
            
            response = sale_order.sudo()._add_products_from_controller(
                    user_id, product_id, action)
            if response:
                return http.Response('CREATED', status=201)
            else:
                return http.Response('NOT FOUND', status=404)

'''
url :- http://localhost:8001/user_cart/
request method:- POST
request parameters :- {"user": 11, "product" : "kurkure", "quantity":2, "action" : "picked"}
response :- status.HTTP_201_CREATED

line_vals = {'product_id': 15, 'name':'test', 'product_uom_qty': 10,
             'price_unit': 30000 }

order_vals = {'partner_id': 57,
              'validity_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
              'order_line': [(0, 0, line_vals)]
              }

so = env['sale.order']
x = so.create(order_vals)'''
