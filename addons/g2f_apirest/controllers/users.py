# pylint: disable=broad-except

import logging
from urllib.parse import urljoin
from datetime import datetime
from json import dumps
import requests
from urllib.parse import urljoin

from odoo import http, _
from odoo.addons.g2f_apirest.controllers.vision_system import VisionSystem
from odoo.exceptions import ValidationError, UserError


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
_logger = logging.getLogger(__name__)


class ResUser(http.Controller):


    def parse_dumps(self, object):
        """Parse fields for dumps response."""

        if isinstance(object, datetime):
            return object.__str__()

        if isinstance(object, bytes):
            return object.decode('ascii')

    @http.route(['/users/new/login'], type='json', auth='user',
                methods=['POST'], website=True, csrf=False)
    def new_login(self, **kw):
        """New login user."""

        server = http.request.env['ir.config_parameter'].sudo().search([
            ('key', '=', 'web.base.url')])

        url_sesion = urljoin(server.value, "/web/session/authenticate")
        headers_login = {'content-type': 'application/json'}
        database = kw.get("db")
        login = kw.get("login")
        password = kw.get("password")

        body = {"jsonrpc": "2.0",
                "params": {
                    "db": database, "login": login, "password": password}
                }
        session = requests.post(url_sesion, data=dumps(body),
                                headers=headers_login
                                )
        session_id = session.cookies.get('session_id')
        return session_id

    @http.route(['/users/get_transaction/last'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def get_last_transaction_by_user(self, **kw):
        """Get last transactions by user betewn app mpbile acces control and
        vision_system."""

        method = http.request.httprequest.method
        login = kw.get('login')
        user = self._validate_user(login)
        transaction = http.request.env['apirest.transaction']

        if method == 'GET' and user:
            transaction = transaction.sudo().get_last_transaction_by_user(
                    login)
            _logger.info(transaction)
            return dumps(transaction[0] if transaction else [], default=self.parse_dumps)

        return http.Response('NOT FOUND', status=404)

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

    @http.route(['/store/get_list'], type='http', auth='public',
                methods=['GET'], website=True, csrf=False)
    def store_list(self):
        """Endpoint return Store list for app moblie."""

        method = http.request.httprequest.method

        stores = []
        store_list = http.request.env['stock.warehouse'].sudo().search(
                [('active', '=', True)]
                )
        results = [(
                [i.store_image for i in f.store_image_ids],
                f.name, f.direccion_local, f.country_id.name,
                f.state_id.name, f.code, f.store_stage, f.store_plano_sav,
                f.store_image
            )
            for f in store_list
            ]

        headers = [
                'otras_imagenes','name', 'direccion_local', 'country_id',
                'state_id', 'code', 'store_stage', 'store_plano_sav',
                'store_image'
            ]
        for result in results:
            stores.append(dict(zip(headers, result)))

        return dumps(stores, default=self.parse_dumps)

    @http.route(['/users/Countries'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def countries_list(self, **kw):
        """Endpoint return Countries list for app moblie."""

        method = http.request.httprequest.method
        country = kw.get('country')
        res_partner = http.request.env['res.partner']
        return dumps(res_partner.sudo().search_country_info(country))

    @http.route(['/users/afip_responsibility_types'], type='http', 
            auth='public', methods=['GET'], website=True, csrf=False)
    def afip_responsibility_types_list(self, **kw):
        """Endpoint return afip_responsibility_types_list for app moblie."""

        method = http.request.httprequest.method
        if method != 'GET':
            return False

        res_partner = http.request.env['res.partner']
        return dumps(
                res_partner.sudo().list_l10n_ar_afip_responsability_type())

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
        """Endpoint when user get list TDC. DEPRECATED. cambiar metodo a POST y utilizar /users/get_payment_cards"""

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

    @http.route(['/users/get_payment_cards'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def get_list_payment_cards(self, **kw):
        """Endpoint when user get list TDC."""

        method = http.request.httprequest.method

        login = kw.get('login')
        user = self._validate_user(login)

        if not user:
            msg = _('User dont exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if method == 'POST':
            response = {'status': '200', 'data': user.partner_id.get_payment_card()}
            return response

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

    @http.route(['/users'], type='http', auth='public',
                methods=['GET'],
                website=True, csrf=False)
    def validate_res_user(self, **kw):
        """Endpoint for register and update data User from app mobile."""

        method = http.request.httprequest.method
        msg = _('User dont exists!')
        login = kw.get('login')
        vat = kw.get('vat')
        identification_type = kw.get('identification_type')
        res_partner = http.request.env['res.partner'].sudo()

        if method == 'GET':
            if res_partner.validate_user(login):
                msg = _('Email User already exists!')

            if res_partner.document_exist(identification_type, vat):
                msg = _('Document User already exists!')

            if res_partner.document_exist(identification_type, vat) and \
                    res_partner.validate_user(login):
                msg = _('Email and Document already exists!')

        response = {'status': '200', 'messsage': msg}
        return dumps(response)

    @http.route(['/users'], type='json', auth='public',
                methods=['POST', 'PUT', 'DELETE'],
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

    def update_user(self, params):
        login = params.get('login')
        user = self._validate_user(login)
        address = params.get('address')
        gender = params.get('gender')
        # business_name = params.get('business_name')
        mobile = params.get('mobile')
        email_recipe_receive = params.get('email_recipe_receive') or False
        country = params.get('country')
        country_state = params.get('country_state')
        state_city = params.get('state_city')
        self.res_partner = user.partner_id
        country_id, state_id = self.res_partner.search_country_state_by_name(
                country, country_state)

        data = {'gender': gender, 'mobile': mobile, 'phone': mobile,
                'street': address,
                'email_recipe_receive': email_recipe_receive,
                'country_id': country_id, 'state_id': state_id,
                'city': state_city}



        if not user:
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        try:
            user.partner_id.write(data)
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
        phone = params.get('mobile')
        business_name = params.get('business_name')
        address = params.get('address')
        identification_type = params.get('identification_type')
        afip_responsibility_type_id = int(params.get('afip_responsability_type_id')) or 0
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
            msg = _('Email User already exists!')
            response = {'status': '400', 'message': msg}
            return dumps(response)

        if (user.partner_id.sudo().document_exist(identification_type, vat) and not user_inactive):
            msg = _('There is already a registered user with this Document!')
            response = {'status': '400', 'message': msg}
            return dumps(response)

        search_identification_type = self.res_partner.sudo().search_identification_type(identification_type)
        identification_type_ = search_identification_type.id if search_identification_type else None

        country_id, state_id = self.res_partner.search_country_state_by_name(country, country_state)

        # Validar aqui como se va amar el nombre, apellido o razon social:
        if afip_responsibility_type_id == 1:
            # Si es Iva responsable inscripto
            print('Responsable inscripto')
        elif afip_responsability_type_id == 5:
            # Si es Consumidor Final
            print('Consumidor final')
        elif afip_responsibility_type_id == 6:
            # Si es resonsable Monotributo
            print('Responsable monotributo')
        else:
            # Se coloca uno por defecto (Consumidor final)
            print('Consumidor final')

        try:
            if not self._validate_user(login) and not user_inactive:
                user.sudo().create({
                    'login': login,
                    'email': login,
                    'password': passw,
                    'name': name,
                    'lastname': lastname,
                    'sel_groups_1_9_10':9
                })
                user._cr.commit()

            if user_inactive:
                user_inactive.sudo().write({'password': passw, 'active': True})
                user_inactive._cr.commit()

            # Update data in respartner
            data = {'birthday': birthday, 'gender': gender, 'mobile': mobile, 'phone': mobile,
                    'street': address, 'l10n_latam_identification_type_id': identification_type_,
                    'vat': vat, 'country_id': country_id, 'state_id': state_id,
                    'city': state_city, 'l10n_ar_afip_responsibility_type_id': afip_responsibility_type_id,
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
        return {"status": "200", "messsage": "ok", "data": user_data}

    def build_response(self, entity, status=200):
        """Build response by all responses tha app mobile or access control."""

        response = dumps(entity, ensure_ascii=False).encode('utf8')
        return http.Response(response,
                             content_type='application/json; charset=utf-8',
                             status=status)

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
