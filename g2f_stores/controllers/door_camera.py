from odoo import http
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StoreDoorCam(http.Controller):

    @http.route(['/store/get_door_cam'], type="http", auth="public", website=True, method=['GET'],
                csrf=False)
    def get_door_cam(self, **kw):
        method = request.httprequest.method
        store_id = kw.get('store_id')
        doors = request.env['store.door'].sudo().search([("store_id.name", "=", store_id)])
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

        return dumps(data)
