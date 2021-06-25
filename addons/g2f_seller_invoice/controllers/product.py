# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from json import dumps
import requests
from odoo import http, _
import json
import logging
_logger = logging.getLogger(__name__)


class Product(http.Controller):
    @http.route('/product/widget/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def listoner(self, **kw):
        vals = {}
        code = kw.get('code')
        product_tmpl = http.request.env['product.template']
        response = product_tmpl.sudo()._get_product_widget(code)
        print(http.request.params)
        print(response)
        # return json.dumps({"result": "Success"})
        return response

# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def get_product_data(self, vals):
#         domain = [('type', '=', 'product')]
#         data = {"dataList": []}
#         if vals:
#             domain = [
#                 ('default_code', '=', vals['sku']),
#                 ('type', '=', 'product')
#             ]
#         product_ids = self.search(domain)
#         for product in product_ids:
#             second_line = product.brand + ' ' if product.brand else ''
#             second_line += str(product.contents) + ' ' if product.contents else ''
#             second_line += product.uom_id.name
#             head = {
#                 "stationCode": "G2F",
#                 "id": product.default_code,
#                 "name": product.name,
#                 "nfc": "https://minigo-visual-impairment.s3-sa-east-1.amazonaws.com/iTANKRDes.mp3",
#                 "originPrice": False,
#                 "salePrice": False,
#                 "discountPercent": False,
#                 "data": {
#                     "ARTICLE_ID": product.default_code,
#                     "ITEM_FIRST_LINE": product.desc_tag,
#                     "ITEM_SECOND_LINE": second_line,
#                     "SALE_PRICE": str(product.list_price),
#                     "LITER_PRICE": "0",
#                     "WEIGHT_UNIT": "0"
#                 }
#             }
#             data["dataList"].append(head)
#         if not product_ids:
#             data = 'No se encontró producto registrado con el SKU: %s' % vals['sku']
#         return data


class ProductTemplate(http.Controller):
    @http.route(['/product/widget'], type='http', auth='public',
                methods=['POST'], csrf=False)
    def get_product_widget(self, **kw):
        code = kw.get('code')
        print(http.request.params)
        print(code)
        return 'Respuesta esperada...'

    #curl --location --request GET 'http://127.0.0.1:8075/camera_ports/?ai_unit=1' --header 'Content-Type: application/json' --data-raw