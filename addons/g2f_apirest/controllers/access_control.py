# pylint: disable=broad-except

import requests
from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class AccessControl(http.Controller):
    """Access Control Controller."""

    @http.route(['/get_message_access_control'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def message_from_access_control(self, **kw):
        """get message from access control."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        transaction = http.request.env['apirest.transaction']

        login = kw.get('userId')
        store_id = kw.get('storeCode')
        door_id = kw.get('doorId')
        code = kw.get('code')
        message = kw.get('message')

        if method == 'POST':
            if code == 7:
                # Crear la sale order
                sale_order = http.request.env['sale.order']
                user = http.request.env['res.partner'].sudo().validate_user(login)
                sale_order.sudo().create_sale_order(user.partner_id.id)

            # tomar el mensaje y guardarlo en el model transaction
            transaction.sudo().create_transaction(login, store_id, door_id, code, message, 'access_control')
            print(login, message)
            # Le respondo a control de acceso que todo esta bien
            response = {'status': '200', 'message': 'OK'}
            return dumps(response)

        response = {'status': '400', 'message': 'NOT FOUND'}
        return dumps(response)

    @http.route(['/users/send_message_access_control'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def send_message_to_access_control(self, **kw):
        """recive from app mobile and send message to access control."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        if method == 'POST':
            # Get params from app mobile
            login = kw.get('login')
            store_id = kw.get('store_id') or 1
            door_id = kw.get('door_id') or 0
            was_confirmed = kw.get('was_confirmed')
    
            # Prepare send to Access control server
            url = 'http://minigo001.ngrok.io/api/Odoo/ConfirmAtHall'
            params = {"storeCode": int(store_id), "doorId": int(door_id),
                      "userId": login, "WasConfirmed": was_confirmed}
            send_access_store_response = requests.post(url, json=params)
            print(send_access_store_response)
