# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
import logging
_logger = logging.getLogger(__name__)


class StorePlano(http.Controller):
    @http.route('/store/plano/', type='json', auth="none", methods=['GET'], cors="*", csrf=False)
    def set_plano(self, **kw):
        code = kw.get('code')
        store = http.request.env['product.store']
        response = store.sudo()._set_plano(kw)
        print(http.request.params)
        print(response)
        # return json.dumps({"result": "Success"})
        _logger.info("### TRAMA ### %r", response)
        return response
