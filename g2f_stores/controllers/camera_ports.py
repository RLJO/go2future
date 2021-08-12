from odoo import http
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StoreCameraPorts(http.Controller):

    @http.route(['/store/camera_ports'], type="http", auth="public", website=True, method=['GET'],
                csrf=False)
    def get_camera_ports(self, **kw):
        method = request.httprequest.method
        #kw = request.jsonrequest
        ai_unit = int(kw.get('ai_unit'))
        camera_obj = http.request.env['store.camera']
        response = {"id": ai_unit, "status": 200, "data": []}
        data = []
        if method == 'GET':
            data = camera_obj.sudo().get_camera_by_ai_unit(ai_unit)
            if data:
                response['data'] = data  # values.update({'data': data})
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return dumps(response)
