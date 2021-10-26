# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
import logging
_logger = logging.getLogger(__name__)


class StorePlano(http.Controller):

    @http.route('/store/plano', type='json', auth="none", methods=['POST'], website=True, csrf=False)
    def set_plano(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        if method == 'POST':
            data = kw.get('data')
            store = http.request.env['product.store']
            response = store.sudo()._set_plano(data)
            _logger.info(" * Llamada de API planogrametria %s", response)
            return response
        else:
            return http.Response('NOT FOUND', status=404)
