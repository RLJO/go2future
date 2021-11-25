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

    @http.route(['/store/plano_shelf_positions'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def plano_shelf_positions(self, **kw):
        """
        THIS CONTROLER sends the data of gondolas and shelf positions given a store code or id or name
        :param kw:
        :return: position data of gondolas and shelf
        """
        method = http.request.httprequest.method
        # kw = http.request.jsonrequest
        response = {"status": 200, "data": []}
        _logger.debug("Init call api /store/plano_shelf: %s" % response)
        if method == 'POST':
            # kw = http.request.jsonrequest
            store = kw.get('store')
            obj = request.env['store.raspi'].sudo()
            res = obj.get_plano_shelf_data(store)
            if res:
                response['success'] = True
                response['error_code'] = 0
                response['data'] = res
            else:
                _logger.info("No data found api /store/plano_shelf: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'
        return response

    @http.route(['/store/plano_shelf'], type='json', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def post_plano_shelf_data(self, **kw):
        """
        THIS CONTROLER sends the data of gondolas and shelf positions given a store code or id or name
        :param kw:
        :return: position data of gondolas and shelf
        """
        method = http.request.httprequest.method
        # kw = http.request.jsonrequest
        response = {"status": 200, "data": []}
        _logger.debug("Init call api /store/plano_shelf: %s" % response)
        if method == 'GET':
            # kw = http.request.jsonrequest
            store = kw.get('store')
            obj = request.env['store.raspi'].sudo()
            res = obj.get_plano_shelf_data(store)
            if res:
                response['success'] = True
                response['error_code'] = 0
                response['data'] = res
            else:
                _logger.info("No data found api /store/plano_shelf: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'
        if method == 'POST':
            kw = http.request.jsonrequest
            data = kw.get('data')
            obj = request.env['store.raspi'].sudo()
            res = obj.post_plano_shelf_data(data)
            if res:
                response['error_code'] = res['status']
                response['message'] = res['message']
            else:
                _logger.info("Failed POST api /store/plano_shelf: %s" % response)
        return response
