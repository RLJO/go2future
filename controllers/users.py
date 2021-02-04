# pylint: disable=broad-except

from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError


class ResUser(http.Controller):
    @http.route(['/users'], type='http', auth='public',
                methods=['GET', 'POST', 'PUT', 'DELETE'],
                website=True, csrf=False)
    def res_user(self, **kw):
        method = http.request.httprequest.method
        print(kw)

        if method == 'POST':
            print('Crear usuario')
            response = self.register(kw)
            print(response)
            return response

        if method == 'PUT':
            print('Modificar Usuario')
        if method == 'GET':
            print('Listar, Obtener Usuario')
        if method == 'DELETE':
            print('Eliminar usuario')
        return False

    def register(self, params=''):
        if not params:
            params = {}

        login = params.get('email')
        passw = params.get('password')
        name = params.get('name')
        lastname = params.get('lastname')

        print(login, passw, name, lastname)

        user = http.request.env['res.users']
        if self._validate_user(login):
            msg = _('User already exists!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        try:
            user.sudo().create({
                'login': login,
                'password': passw,
                'name': name,
            })
            user._cr.commit()

            # Update data inm respartner
            self._update_res_partner(login)

            response = {'status': '200', 'messsage': 'ok'}
        except Exception as error_excp:
            msg = _(error_excp)
            response = {'status': '400', 'messsage': msg}
            return dumps(response)
        return dumps(response)

    def _validate_user(self, login=''):
        user = http.request.env['res.users']
        return user.sudo().search([('login', '=', login)])

    def _update_res_partner(self, login):
        user = self._validate_user(login)
        if user:
            data = {'phone': '11111'}
            user.partner_id.write(data)
            user._cr.commit()
            return True
        return False

    @http.route(['/login'], type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def login(self, **kw):
        print(kw)
        login = kw.get('email')
        passw = kw.get('password')

        if not self._validate_user(login):
            msg = _('User does not exist!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        if not self._validate_login(login, passw):
            msg = _('Incorrect user or password!')
            response = {'status': '400', 'messsage': msg}
            return dumps(response)

        # por ahora devuelvo un OK pero deberia devolver un hash
        # luego la app basada en ese hash genera un QR para entrar
        return dumps({'status': '200', 'messsage': 'ok'})

    def _validate_login(self, email, password):
        user = http.request.env['res.users'].sudo().search(
            [('login', '=', email)])
        user_id = user.id
        try:
            user.with_user(user_id)._check_credentials(password, user.env)
            return True
        except Exception as error:
            print(error)
            return False
