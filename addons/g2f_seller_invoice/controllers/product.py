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


class Product(http.Controller):
    @http.route('/product/widget/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_product_widget(self, **kw):
        code = kw.get('code')
        product_tmpl = http.request.env['product.template']
        response = product_tmpl.sudo()._get_product_widget(code)
        print(http.request.params)
        print(response)
        # return json.dumps({"result": "Success"})
        _logger.info("### TRAMA ### %r", response)
        return response

    @http.route('/product/planos/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_product_planos(self, **kw):
        code = kw.get('code')
        product_tmpl = http.request.env['product.template']
        response = product_tmpl.sudo()._get_product_planos(code)
        print(http.request.params)
        print(response)
        _logger.info("### TRAMA ### %r", response)
        return response

# curl -i -X POST -H "Content-Type: application/json" -d '{"params": {"code":"0001"}}' 'https://g2f-api-rest.odoo.com/product/widget/'