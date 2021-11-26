from odoo.http import request
import logging
from odoo import http, _
# from odoo.exceptions import ValidationError, UserError



_logger = logging.getLogger(__name__)


class StoreRasberryPi(http.Controller):

    @http.route(['/store/get_sensor_cart_data'], type="json", auth="public", website=True, method=['GET'], csrf=False)
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

        return response

    @http.route(['/store/post_sensor_calibration'], type='json', auth='public', methods=['POST'], website=True, csrf=False, cors='*')
    def post_sensor_calibration(self, **kw):
        method = http.request.httprequest.method
        sensor = kw.get('sensor')
        c_factor = kw.get('c_factor')
        response = {"id": sensor, "status": 200, "data": []}

        # make a method
        if method == "POST":
            obj = request.env['store.sensor'].sudo()
            res = obj.post_sensor_calibration_data(sensor, c_factor)
            if res:
                response['success'] = True
                response['data'] = res
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return response

    @http.route(['/store/get_gondola_store'], type='json', auth='public', methods=['POST'], website=True, csrf=False, cors='*')
    def get_gondola_store(self, **kw):
        method = http.request.httprequest.method
        store_code = kw.get('store_code')
        response = {"id": store_code, "status": 200, "data": []}
        store_id = request.env['stock.warehouse'].sudo().search([("code", "=", store_code)])
        # make a method
        if method == "POST":
            # obj = request.env['store.sensor'].sudo()
            # res = obj.post_sensor_calibration_data(store)
            # data = request.env['store.sensor'].sudo().search([("store_id", "=", store_id.id)])
            data = http.request.env['store.raspi'].sudo().search_read(
                [("store_id", "=", store_id.id)], fields=['id', 'name', 'ip_add'])
            if data:
                response['success'] = True
                response['data'] = data
            else:
                _logger.info("No data found: %s" % response)
                response['success'] = False
                response['error_code'] = 1
                response['error_data'] = 'No data found!'

        return response