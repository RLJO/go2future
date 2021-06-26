# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from json import dumps
import requests
from odoo import http, _
import json
import logging
_logger = logging.getLogger(__name__)


class Account(http.Controller):
    @http.route('/invoice/confirm/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def invoice_confirm(self, **kw):
        # vals = {}
        # code = kw.get('code')
        account = http.request.env['account.move']
        response = account.sudo()._invoice_confirm(kw)
        print(http.request.params)
        print(response)
        return response

# curl -i -X POST -H "Content-Type: application/json" -d '{"params": {"id":22}}' 'https://g2f-api-rest.odoo.com/pinvoice/confirm/'