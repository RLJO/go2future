from odoo import http
from odoo.http import request
from json import dumps
import logging
_logger = logging.getLogger(__name__)


class StoreRasberryPi(http.Controller):

    @http.route(['/store/get_sensor_cart_data'], type="http", auth="public", website=True, method=['GET'],
                csrf=False)
    def get_sensor_cart_data(self, **kw):
        pi_id = int(kw.get('pi_id'))
        response = {"id": pi_id, "status": 200, "data": []}
        # make a method
        data = request.env['store.sensor'].sudo().search([("pi_id", "=", pi_id)])
        res = data.get_sensor_data(data)

        if res:
            response['success'] = True
            response['data'] = res
        else:
            _logger.info("No data found: %s" % response)
            response['success'] = False
            response['error_code'] = 1
            response['error_data'] = 'No data found!'

        return dumps(response)
