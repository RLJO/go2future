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
        code = kw.get('code')
        message = kw.get('message')

        if method == 'POST':
            print('tomar el mensaje y guardarlo en el model transaction')
            print(code, message)
            values = {'login': login,
                      'code': code,
                      'message': message,
                      'from_app': 'message_from_access_control'}
            transaction.sudo().create(values)
            transaction._cr.commit()
            return http.Response('OK', status=200)

        return http.Response('NOT FOUND', status=404)
