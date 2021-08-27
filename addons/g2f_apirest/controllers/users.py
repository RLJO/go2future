# pylint: disable=broad-except

from json import dumps
import requests
from urllib.parse import urljoin

from odoo import http, _
from odoo.addons.g2f_apirest.controllers.vision_system import VisionSystem
from odoo.exceptions import ValidationError, UserError


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


    @http.route(['/users/Countries'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def countries_list(self, **kw):
        """Endpoint return Countries list for app moblie."""

        method = http.request.httprequest.method
        country = kw.get('country')
        res_partner = http.request.env['res.partner']
        return dumps(res_partner.sudo().search_country_info(country))

    @http.route(['/users/DocumentTypes'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def document_type_list(self, **kw):
        """Endpoint return document_type_list for app moblie."""

        method = http.request.httprequest.method
        res_partner = http.request.env['res.partner']
        return dumps(res_partner.sudo().list_identification_type())

    @http.route(['/users/payment_cards_types'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def payment_cards_type_list(self, **kw):
        """Endpoint return payment_cards_type_list for app moblie."""

        method = http.request.httprequest.method
        res_partner = http.request.env['res.partner']
        return dumps(list(res_partner.sudo().payment_cards_type_list()))

    @http.route(['/users/payment_cards'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def get_payment_cards(self, **kw):
        """Endpoint when user get list TDC."""

        method = http.request.httprequest.method

        login = kw.get('login') 
        user = self._validate_user(login)

        if not user:
            msg = _('User dont exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if method == 'GET':
            response = user.partner_id.get_payment_card()
            return dumps(response)


    @http.route(['/users/payment_cards'], type='json', auth='public',
                methods=['POST', 'PUT', 'PATCH', 'DELETE'],
                website=True, csrf=False)
    def payment_cards(self, **kw):
        """Endpoint when user create new TDC."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        login = kw.get('login')
        card_id = kw.get('id')
        card_name = kw.get('name')
        card_number = kw.get('card_number')
        security_code = kw.get('security_code')
        expiration_month = kw.get('expiration_month')
        expiration_year = kw.get('expiration_year')
        card_type = kw.get('card_type')
        card_identification = kw.get('card_identification')
        state = kw.get('state') or 'disabled'

        vals = {'name': card_name, 'card_number': card_number,
                'security_code': security_code, 'expiration_month': expiration_month,
                'expiration_year': expiration_year, 'card_type': card_type,
                'card_identification': card_identification, 'state': state}

        user = self._validate_user(login)
        if not user:
            msg = _('User dont exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        # Le agrega el partner a los parametros para enviar la solicitud
        vals.update({'partner_id': user.partner_id.id})

        if method == 'POST':
            user.partner_id.create_payment_card(vals)
            response = {"status": "201", "message": "OK"}
            return dumps(response)

        if method == 'DELETE':
            kw.pop('login')
            user.partner_id.delete_payment_card(kw)
            response = {"status": "201", "message": "OK"}
            return dumps(response)

        if method == 'PATCH':
            kw.pop('login')
            user.partner_id.update_payment_card(kw)
            response = {"status": "201", "message": "OK"}
            return dumps(response)

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

        response = {"status": "200", "message": "Wait for access control"}

        if method == 'POST':
            print('Validar que el usuario exista o este activo')
            user = self._validate_user(login)
            if user:
                print(f'El ID del usuario es:{user.id}')
                # Enviarle al sistema de control de acceso que el usaurio entro

                store = http.request.env['stock.warehouse'].sudo().search(
                        [('id', '=', store_id)]
                )
                if not store:
                    msg = _('Store dont exist.')
                    response = {"status": "400", "message": msg}
                    return response

                # Prepare url endpoint and send to Access control server
                base_url = store.access_control_url
                params = {"storeCode": int(store_id),
                          "doorId": int(door_id),
                          "userId": login}
                try:
                    requests.post(base_url, json=params)
                except Exception as Error:
                    response = {"status": "400", "message": Error}

                return dumps(response)

            msg = _('User dont exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

    @http.route(['/users/avatar'], type='json', auth='public', methods=['PUT'],
                website=True, csrf=False)
    def update_user_avatar(self, **kw):
        """Endpoint for update avatar user from app mobile."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        if method == 'PUT':
            login = kw.get('login')
            avatar = kw.get('avatar')
            data = {"user_avatar": avatar}

            response = self._update_res_partner(login, data)
            return response

        return False

    @http.route(['/users'], type='json', auth='public',
                methods=['GET', 'POST', 'PUT', 'DELETE'],
                website=True, csrf=False)
    def res_user(self, **kw):
        """Endpoint for register and update data User from app mobile."""

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

        if method == 'DELETE':
            print('Delete Usuario')
            response = self.delete_user(kw)
            return response
        return False

    def delete_user(self, kw):
        """Delete User."""

        login = kw.get('login')
        user = self._validate_user(login)

        if not user:
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        user.write({'active': False})
        msg = _('User has be deleted!')
        response = {'status': '200', 'messsage': msg}
        return dumps(response)

    def update_user(self, kw):
        login = kw.get('login')
        name = kw.get('name')
        lastname = kw.get('lastname')

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
        mobile = params.get('mobile')
        business_name = params.get('business_name')
        address = params.get('address')
        identification_type = params.get('identification_type')
        vat = params.get('vat')
        country = params.get('country')
        country_state = params.get('country_state')
        state_city = params.get('state_city')
        image_1920 = params.get('image_1920')
        document_obverse = params.get('document_obverse')
        document_reverse = params.get('document_reverse')
        terms_conditions_agreement = params.get('terms_conditions_agreement') or False
        email_recipe_receive = params.get('email_recipe_receive') or False

        user = http.request.env['res.users']
        self.res_partner = user.partner_id
        user_inactive = self._validate_user_inactive(login)

        if self._validate_user(login):
            msg = _('User already exists!')
            response = {'status': '400', 'message': msg}
            return dumps(response)

        if (user.partner_id.sudo().document_exist(identification_type, vat) and not user_inactive):
            msg = _('User already exists!')
            response = {'status': '400', 'message': msg}
            return dumps(response)

        search_identification_type = self.res_partner.sudo().search_identification_type(identification_type)
        identification_type_ = search_identification_type.id if search_identification_type else None

        country_id, state_id = self.res_partner.search_country_state_by_name(country, country_state)

        try:
            if not self._validate_user(login) and not user_inactive:
                user.sudo().create({
                    'login': login,
                    'email': login,
                    'password': passw,
                    'name': name,
                    'lastname': lastname,
                })
                user._cr.commit()

            if user_inactive:
                user_inactive.sudo().write({'password': passw, 'active': True})
                user_inactive._cr.commit()

            # Update data in respartner
            data = {'birthday': birthday, 'gender': gender, 'mobile': mobile,
                    'street': address, 'l10n_latam_identification_type_id': identification_type_,
                    'vat': vat, 'country_id': country_id, 'state_id': state_id,
                    'city': state_city, 'l10n_ar_afip_responsibility_type_id': 5,
                    'image_1920': image_1920, 'document_obverse': document_obverse,
                    'document_reverse': document_reverse, 'lang': 'es_AR',
                    'terms_conditions_agreement': terms_conditions_agreement,
                    'email_recipe_receive': email_recipe_receive}

            self._update_res_partner(login, data)

            response = {'status': '200', 'message': 'ok'}

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

    def _validate_user_inactive(self, login):
        """Validate if user id Inactive."""

        user = http.request.env['res.users']
        return user.sudo().search([('login', '=', login),
                                   ('active', '=', False)]) 

    @http.route(['/users/login'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def login(self, **kw):
        kw = http.request.jsonrequest
        login = kw.get('login')
        passw = kw.get('password')

        if self._validate_user_inactive(login):
            msg = _('User is disabled, you must register again to enable it')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if not self._validate_user(login):
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if not self._validate_login(login, passw):
            msg = _('Incorrect user or password!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        user_data = self._get_data_user(login)
        return dumps({'status': '200', 'messsage': 'ok', 'data': user_data})

    def _get_data_user(self, email):
        user = http.request.env['res.users'].sudo().search(
            [('login', 'ilike', email)]
        )
        res_partner = user.partner_id.sudo().get_data_user()
        return res_partner

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

    def reset_password_by_document(self, kw):
        """reset password by document passed."""

        res_partner = http.request.env['res.partner']
        user = http.request.env['res.users']

        identification_type = kw.get('identification_type')
        vat = kw.get('vat')
        search_identification_type = res_partner.sudo().search_identification_type(identification_type)

        identification_type_id = search_identification_type.id if search_identification_type else ''
        domain = [('l10n_latam_identification_type_id', '=', identification_type_id),
                  ('vat', '=', vat)]
        search_res_partner = res_partner.sudo().search(domain)
        print(search_res_partner.email)
        return search_res_partner.email

    @http.route(['/users/ResetPassword'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def reset_password_user(self, **kw):
        kw = http.request.jsonrequest
        login = kw.get('login') or self.reset_password_by_document(kw)

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
