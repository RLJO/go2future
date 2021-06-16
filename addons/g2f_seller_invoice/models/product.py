# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from json import dumps
import requests
from odoo import http, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_product_data(self, vals):
        domain = [('type', '=', 'product')]
        data = {"dataList": []}
        if vals:
            domain = [
                ('default_code', '=', vals['sku']),
                ('type', '=', 'product')
            ]
        product_ids = self.search(domain)
        for product in product_ids:
            second_line = product.brand + ' ' if product.brand else ''
            second_line += str(product.contents) + ' ' if product.contents else ''
            second_line += product.uom_id.name
            head = {
                "stationCode": "G2F",
                "id": product.default_code,
                "name": product.name,
                "nfc": "https://minigo-visual-impairment.s3-sa-east-1.amazonaws.com/iTANKRDes.mp3",
                "originPrice": False,
                "salePrice": False,
                "discountPercent": False,
                "data": {
                    "ARTICLE_ID": product.default_code,
                    "ITEM_FIRST_LINE": product.desc_tag,
                    "ITEM_SECOND_LINE": second_line,
                    "SALE_PRICE": str(product.list_price),
                    "LITER_PRICE": "0",
                    "WEIGHT_UNIT": "0"
                }
            }
            data["dataList"].append(head)
        if not product_ids:
            data = 'No se encontró producto registrado con el SKU: %s' % vals['sku']
        return data


# class ProductTemplate(http.Controller):
#     @http.route(['/update_gondola'], type='http', auth='public',
#                 methods=['POST'], website=True, csrf=False)
#     def update_gondola(self):
#         return 'Ejecutar aqui un post a la API de los indios'

    #curl --location --request GET 'http://127.0.0.1:8075/camera_ports/?ai_unit=1' --header 'Content-Type: application/json' --data-raw