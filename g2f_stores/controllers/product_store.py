# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StorePlano(http.Controller):

    @http.route('/store/plano', type='json', auth="none", methods=['POST'], website=True, csrf=False)
    def set_plano(self, **kw):
        """
        THIS CONTROLER POST THE INFORMATION FROM UNREAL TO PRODUCT IN PLANOGRAM
        METHOD POST: Change the products in plano given a store code.
        METHOD GET: Send the products and position in plano given a store code.
        """
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        if method == 'POST':
            data = kw.get('data')
            store = http.request.env['product.store']
            response = store.sudo()._set_plano(data)
            _logger.info(" * Llamada de API planogrametria %s", response)
            return response
        elif method == 'GET':
            return http.Response('NOT FOUND', status=404)
        else:
            return http.Response('NOT FOUND', status=404)

    @http.route(['/store/plano_shelf'], type="json", auth="public", website=True, method=['GET'], csrf=False)
    def get_sensor_cart_data(self, **kw):
        """
        THIS CONTROLER sends the data of gondolas and shelf positions given a store code or id or name
        :param kw:
        :return: position data of gondolas and shelf
        """
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        store = kw.get('store')
        response = {"status": 200, "data": []}
        if method == 'GET':
            # make a method
            data = request.env['store.raspi'].sudo()
            res = data.get_plano_shelf_data(store)
            if res:
                response['success'] = True
                response['error_code'] = 0
                response['data'] = res
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return response
