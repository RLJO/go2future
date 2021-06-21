# pylint: disable=broad-except

from json import dumps
import requests

from odoo import http, _
from odoo.addons.g2f_apirest.controllers.vision_system import VisionSystem
# from odoo.exceptions import ValidationError, UserError


class ResUser(http.Controller):
    @http.route(['/users/get_transaction'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def get_transaction(self, **kw):
        """Get all notifications send by acces control and vision_system."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        login = kw.get('login')
        store_id = kw.get('store_id')
        user = self._validate_user(login)
        transaction = http.request.env['apirest.transaction']

        if method == 'POST' and user:
            transactions = transaction.sudo().get_transaction_by_user(login, store_id)
            print(transactions)
            return dumps(transactions)

        return http.Response('NOT FOUND', status=404)

    @http.route(['/users/EnterStore'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def enter_store(self, **kw):
        """Endpoint when user enter Store."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        login = kw.get('login')
        door_id = kw.get('door_id')
        store_id = kw.get('store_id')

        if method == 'POST':
            print('Validar que el usuario exista o este activo')
            user = self._validate_user(login)
            if user:
                print(f'El ID del usuario es:{user.id}')
                # Enviarle al sistema de control de acceso que el usaurio entro
                url = "http://minigo001.ngrok.io/api/Odoo/OpenDoor"
                params = {"storeCode": int(store_id), "doorId": int(door_id), "userId": login}
                try:
                    # enter_store_response = requests.post(url, json=params)
                    print(enter_store_response.text)
                except Exception as E:
                    print(f'Error:{E}')

                response = {"status": "200", "message": "Wait for access control"}
                return dumps(response)

            msg = _('User dont exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

    @http.route(['/users'], type='json', auth='public',
                methods=['GET', 'POST', 'PUT', 'DELETE'],
                website=True, csrf=False)
    def res_user(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        if method == 'POST':
            print('Crear usuario')
            response = self.register(kw)
            print(response)
            return response
        if method == 'PUT':
            print('Modificar Usuario')
            response = self.update_user(kw)
            return response
        if method == 'GET':
            print('Listar, Obtener Usuario')
        if method == 'DELETE':
            print('Eliminar usuario')
        return False

    def update_user(self, kw):
        login = kw.get('login')
        name = kw.get('name')
        lastname = kw.get('lastname')

        # Aqui se toman los datos de la tarjeta de credito
        # name
        # card_number
        # security_code
        # expiration_month
        # expiration_year
        # card_type
        # card_identification
        # state

        user = self._validate_user(login)
        if not user:
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        try:
            user.sudo().write({'name': name, 'lastname': lastname})
            user._cr.commit()
            response = {'status': '200', 'message': 'ok'}
        except Exception as error_excp:
            response = {'status': '400', 'message': _(error_excp)}

        return dumps(response)

    def register(self, params=''):
        if not params:
            params = {}

        login = params.get('login')
        passw = params.get('password')
        name = params.get('name')
        lastname = params.get('lastname')
        birthday = params.get('birthday')
        gender = params.get('gender')
        phone = params.get('phone')
        business_name = params.get('business_name')
        address = params.get('address')
        
        # Nuevos campos
        # identification_type = data.get('identification_type')
        # vat = data.get('vat')


        user = http.request.env['res.users']
        if self._validate_user(login):
            msg = _('User already exists!')
            response = {'status': '400', 'message': msg}
            return dumps(response)

        try:
            new_user = user.sudo().create({
                'login': login,
                'email': login,
                'password': passw,
                'name': name,
                'lastname': lastname,
            })
            user._cr.commit()

            # Update data in respartner
            data = {'birthday': birthday, 'gender': gender, 'phone': phone,
                    'street': address}
            self._update_res_partner(login, data)

            response = {'status': '200', 'message': 'ok'}

            # Send data to Vision System
            # VisionSystem.customer_entry(new_user)

        except Exception as error_excp:
            msg = _(error_excp)
            response = {'status': '400', 'message': msg}
            return dumps(response)
        return dumps(response)

    def _validate_user(self, login=''):
        user = http.request.env['res.users']
        return user.sudo().search([('login', '=', login)])

    def _update_res_partner(self, login, data):
        user = self._validate_user(login)

        if user:
            user.partner_id.write(data)
            user._cr.commit()
            return True
        return False

    @http.route(['/users/login'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def login(self, **kw):
        kw = http.request.jsonrequest
        login = kw.get('login')
        passw = kw.get('password')

        if not self._validate_user(login):
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if not self._validate_login(login, passw):
            msg = _('Incorrect user or password!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)
        else:
            user_data = self._get_data_user(login)

        # por ahora devuelvo un OK y los datos del usuario,
        # pero deberia devolver un hash
        # luego la app basada en ese hash genera un QR para entrar
        return dumps({'status': '200', 'messsage': 'ok', 'data': user_data})

    def _get_data_user(self, email):
        user = http.request.env['res.users'].sudo().search_read(
            [('login', 'ilike', email)], ['login', 'name', 'lastname'])

        return user[0] if user else ''

    def _validate_login(self, login, password):
        user = http.request.env['res.users'].sudo().search(
            [('login', '=', login)])
        user_id = user.id
        try:
            user.with_user(user_id)._check_credentials(password, user.env)
            return True
        except Exception as error:
            print(error)
            return False

    @http.route(['/users/ResetPassword'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def reset_password_user(self, **kw):
        kw = http.request.jsonrequest
        login = kw.get('login')
        user = self._validate_user(login)

        if not user:
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        try:
            user.reset_password(user.login)
            response = {'status': '200', 'message': 'ok'}
        except Exception as error_reset_password:
            response = {'status': '400', 'message': _(error_reset_password)}

        return dumps(response)
