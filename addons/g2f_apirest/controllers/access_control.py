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
            if code == 1:
                # message = _('More than one person in the entrance hall')
                pass
            elif code == 2:
                # message = _('Confirm that you want to enter the store?')
                pass
            elif code == 3:
                # message = _('No quiere entrar?')
                pass
            elif code == 4:
                # message = _('Now you can enter the store')
                pass
            elif code == 5:
                # message = _('User already entered the store')
                # Crear la sale order
                sale_order = http.request.env['sale.order']
                user = http.request.env['res.partner'].sudo().validate_user(login)
                sale_order.sudo().create_sale_order(user.partner_id.id)
            else:
                return http.Response('NOT FOUND', status=404)

            # tomar el mensaje y guardarlo en el model transaction
            # transaction.sudo().create_transaction(login, store_id, door_id, code, message, 'access_control')
            print(login, message)
            # Le respondo a control de acceso que todo esta bien
            response = {'status': '200', 'message': 'OK'}
            return dumps(response)

        response = {'status': '400', 'message': 'NOT FOUND'}
        return dumps(response)

    @http.route(['/send_message_access_control'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def send_message_to_access_control(self, **kw):
        """recive from app mobile and send message to access control."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        if method == 'POST':
            # Get params from app mobile
            login = kw.get('userId')
            store_id = kw.get('storeCode')
            was_confirmed = kw.get('WasConfirmed')
    
            # Prepare send to Access control server
            url = 'http://minigo001.ngrok.io/api/Odoo/ConfirmAtHall'
            params = {'storeCode': store_id, 'doorId': door_id, 'userId': login, WasConfirmed: was_confirmed}
            send_access_store_response = requests.post(url, data=params)
            print(send_access_store_response)
