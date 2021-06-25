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
    def get_product_widget(self, vals):
        data = {"data": []}
        pricelist = self.env['product.pricelist.item']
        location_ids = self.env['stock.location'].search([('location_id.name', '=', vals['code'])])
        quant = self.env['stock.quant']
        quant_ids = quant.search([('location_id', 'in', location_ids.ids)], order='location_id')
        for line in quant_ids:
            second_line = line.product_id.brand + ' ' if line.product_id.brand else ''
            second_line += str(line.product_id.contents) + ' ' if line.product_id.contents else ''
            second_line += line.product_id.uom_id.name
            deals = pricelist.search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('website_deals_m2o.state', '=', 'validated')
            ])
            # discounted_price, percent_price = self.get_deals(line)
            if deals:
                discounted_price = deals.discounted_price
                percent_price = deals.percent_price
            else:
                discounted_price = 0.0
                percent_price = 0.0
            head = {
                "ARTICLE_ID": line.product_id.barcode,
                "ITEM_STOCK": line.quantity,
                "ITEM_FIRST_LINE": line.product_id.desc_tag,
                "ITEM_SECOND_LINE": line.product_id.desc_tag_2,
                "ITEM_BRAND": line.product_id.brand,
                "ITEM_VOLUME": line.product_id.contents,
                "ITEM_VOLUME_MEASUREMENT": line.product_id.uom_id.name,
                "ITEM_PRICE": str(line.product_id.list_price),
                "ITEM_REFERENCE_PRICE": line.product_id.uom_price.split()[1],
                "ITEM_REFERENCE_PRICE_MEASUREMENT": line.product_id.uom_price.split()[0],
                "ITEM_LOCATION": vals['code'] + '/' + line.location_id.name,

                "OFFER": {
                    "SALE_PRICE": discounted_price,
                    "SALE_PERCENT": percent_price
                }
            }
            data["data"].append(head)
        if not quant_ids:
            data = 'No se encontró Minigo registrado con el id: %s' % vals['code']
        return data

    # def get_deals(self, product_id):
    #     lis = []
    #     control = []
    #     pricelist = self.env['product.pricelist.item']
    #     deals = pricelist.search([
    #         ('product_tmpl_id', '=', product_id.product_tmpl_id.id),
    #         ('website_deals_m2o.state', '=', 'validated')
    #     ])
    #     for l in pricelist:
    #         for lines in deals:
    #             detail = deals.filtered(lambda x: x.product_tmpl_id == lines.product_id.product_tmpl_id)
    #             # raise UserError(_('RESULT. %r') % detail)
    #             if detail not in control:
    #                 if len(detail) > 1:
    #                     weight = sum([pro.weight for pro in detail])
    #                     dct = {
    #                         'product_id': l.product_id.id,
    #                         'type_id': detail[0].product_id.id,
    #                         'weight': weight,
    #                     }
    #                 else:
    #                     dct = {
    #                         'product_id': l.product_id.id,
    #                         'type_id': detail.product_id.id,
    #                         'weight': detail.weight,
    #                     }
    #                 lis.append((0, 0, dct))
    #                 control.append(detail)
    #     self.type_summary_ids = lis


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
#     @http.route(['/product/list'], type='http', auth='public',
#                 methods=['POST'], website=True, csrf=False)
#     def get_product_data_list(self):
#         return 'Ejecutar aqui un post a la API de los indios'

    #curl --location --request GET 'http://127.0.0.1:8075/camera_ports/?ai_unit=1' --header 'Content-Type: application/json' --data-raw