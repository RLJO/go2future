# pylint: disable=broad-except

import requests
from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class VisionSystem(http.Controller):
    @http.route(['/customer_order_entry'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def customer_order_entry(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        customer = kw.get('customer')
        products = kw.get('products')  # Ej: {"parle": 5, "hair oil":2},
        transaction_id = kw.get('transaction_id')
        grand_total = kw.get('grand_total')

        if method == 'POST':
            print('Insertar en Odoo los datos del cliente y productos')
            print(customer, products, transaction_id, grand_total)

    @staticmethod
    def customer_entry(user_instance):
        userid = user_instance.id
        first_name = user_instance.name
        last_name = user_instance.lastname
        email = user_instance.email
        age = user_instance.partner_id.age()
        gender = user_instance.gender
        contact_no = user_instance.phone
        address = user_instance.street

        payload = {"userid": userid, "first_name": first_name,
                   "last_name": last_name, "email": email, "age": age,
                   "gender": gender, "contact_no": contact_no,
                   "address": address
                   }
        url = 'http://localhost:8000/customer_entry/'
        response = requests.post(url, json=payload)
        # response :- status.HTTP_201_CREATED
        return response
