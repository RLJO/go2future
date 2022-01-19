from odoo import http
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StoreDoorCam(http.Controller):

    @http.route(['/store/get_door_cam'], type="json", auth="public", website=True, method=['GET'],
                csrf=False)
    def get_door_cam(self, **kw):
        method = request.httprequest.method
        store_id = kw.get('store_id')
        doors = request.env['store.door'].sudo().search([("store_id.code", "=", store_id)])
        response = {"id": store_id, "status": 200, "data": []}
        data = {}
        if method == 'GET':
            data = doors.get_door_cam(doors)

            if data:
                response['success'] = True
                response['data'] = data  # values.update({'data': data})
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return response

    @http.route(['/store/get_store_cams'], type="json", auth="public", website=True, method=['POST'], csrf=False)
    def get_store_cam(self, **kw):
        method = request.httprequest.method
        store_id = kw.get('store_code')
        cameras = request.env['store.camera'].sudo().search_read([("store_id.code", "=", store_id)],
                                                                 fields=['name', 'device_url', 'port_number'])
        response = {"id": store_id, "status": 200, "data": []}
        data = {}
        if method == 'POST':
            data = cameras
            if data:
                response['success'] = True
                response['data'] = data  # values.update({'data': data})
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return response

