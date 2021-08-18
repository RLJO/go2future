from odoo import http
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class GetStoreZones(http.Controller):

    @http.route(['/store/get_zones'], type="http", auth="public", website=True, method=['GET'],
                csrf=False)
    def get_store_zones(self, **kw):
        method = request.httprequest.method
        store_id = int(kw.get('store_id'))
        response = {"id": store_id, "status": 200, "data": []}
        data = request.env['camera.zone'].sudo().search([("id", "=", int(store_id))])
        if method == 'GET':
            if data:
                response['success'] = True
                response['return'] = "Something"
            else:
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return dumps(response)
