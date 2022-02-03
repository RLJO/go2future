# -*- coding: utf-8 -*-
from odoo import http, _
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StorePlanoSav(http.Controller):
    @http.route(['/store/post_sav_file'], type='json', auth='public', methods=['POST'], website=True, csrf='*')
    def post_sav_file(self, **kw):
        method = http.request.httprequest.method
        store = kw.get('code')
        obj_store = http.request.env['stock.warehouse'].sudo()
        if type(store) == int:
            store_id = obj_store.search([('id', '=', store)])
        else:
            store_id = obj_store.search([('code', '=', store)])
        if not store_id:
            return http.Response('NOT FOUND', status=404)
        if method == 'POST':
            file_sav = kw.get('file_sav')
            store_id.write({'store_plano_sav': file_sav})
            _logger.info(" * Llamada de API  post_sav_file para store %s", store_id.code)
            response = {"status": 200, 'error_code': 0, "error_message": ['Se guardo de forma correcta']}
            return response

    @http.route(['/store/get_sav_file'], type='json', auth='public', methods=['POST'], website=True, csrf='*')
    def get_sav_file(self, **kw):
        method = http.request.httprequest.method
        store = kw.get('code')
        obj_store = http.request.env['stock.warehouse'].sudo()
        if type(store) == int:
            store_id = obj_store.search([('id', '=', store)])
        else:
            store_id = obj_store.search([('code', '=', store)])
        if not store_id:
            return http.Response('NOT FOUND', status=404)
        if method == 'POST':
            file_sav = kw.get('file_sav')
            data = {'store_plano_sav': store_id.store_plano_sav}
            _logger.info("get_sav_file para store %s", store_id.code)
            response = {"status": 200, 'data': data}
            return response


class StoreCameraVision(http.Controller):
    @http.route(['/store/get_cameras'], type='json', auth='api_key', methods=['GET'], website=True, csrf=False)
    def get_cameras(self, **kw):      ############# Controlador que NO SE USA #############
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        print(kw)
        store_id = kw.get('store_id')
        if type(store_id) == str:
            store_id = http.request.env['stock.warehouse'].sudo().search([('code', '=', store_id)]).id
        if method == 'GET':
            data = http.request.env['store.camera'].sudo().search_read(
                [("store_id", "=", store_id)], fields=['id', 'name', 'device_url', 'port_number'])
            return {"status": 200, "data": [data]}

