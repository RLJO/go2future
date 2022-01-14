import json

from odoo import http
from odoo.http import request


class ModelName(http.Controller):

    @http.route(['/online_shopping_app/sale_create'], type="json", auth="public", website=True,
                method=['POST'], csrf=False)
    def sale_order_create(self, **kw):
        values = {}

        data = request.env['sale.order'].sudo().sale_create(kw)

        if data:
            values['success'] = True
            values['return'] = "Shopping car created"
            values['data'] = data
        else:
            values['success'] = False
            values['error_code'] = 1
            values['error_data'] = 'No data found!'

        return values
