import json

from odoo import http
from odoo.http import request


class IAModelController(http.Controller):

    @http.route(['/store/get_ia_models'], type="json", auth="public", website=True, method=['POST'], csrf=False)
    def get_ia_models(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        if method == 'POST':
            data = http.request.env['product.iamodel'].sudo().search_read(fields=['name'])
            return {"status": 200, "data": [data]}
