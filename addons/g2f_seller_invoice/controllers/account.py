# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from json import dumps
import requests
from odoo import http, _
import time
import json
import logging
_logger = logging.getLogger(__name__)


class Account(http.Controller):
    @http.route('/invoice/confirm/', type='json', auth="public", methods=['POST'], cors="*", csrf=False)
    def invoice_confirm(self, **kw):
        account = http.request.env['account.move']
        response = account.sudo()._invoice_confirm(kw)
        print(http.request.params)
        print(response)
        return response

    @http.route('/invoice/search/', type='json', auth="public", methods=['POST'], cors="*", csrf=False)
    def invoice_search(self, **kw):
        res = []
        account = http.request.env['account.move']
        moves = account.sudo().search([
            ('state', '=', 'posted'),
            ('invoice_date', '>=', kw['start_date']),
            ('invoice_date', '<=', kw['end_date'])
        ])
        for invoice in moves:
            items = []
            inv_date = time.strftime("%d/%m/%y")
            inv_time = time.strftime("%H:%M:%S")
            name = invoice.partner_id.name.split()
            first_name = ''
            last_name = ''
            if len(name) == 2:
                first_name = name[0]
                last_name = name[1]
            if len(name) >= 3:
                first_name = name[0] + ' ' + name[1]
                last_name = name[2]
                if len(name) == 4:
                    last_name += ' ' + name[3]

            for line in invoice.invoice_line_ids:
                for tax in line.tax_ids:
                    tax_items = {
                        "name": tax.name,
                        "amount": tax.amount
                    }
                item = {
                    "EAN13": line.product_id.barcode,
                    "product": line.name,
                    "sku_code": line.product_id.default_code,
                    "quantity": line.quantity,
                    "unit_price": line.price_unit,
                    "discount": line.discount,
                    "tax": tax_items,
                    "subtotal": line.price_subtotal
                }
                items.append(item)

            data = {
                "id": invoice.id,
                "name": first_name,
                "last_name": last_name,
                "consumer_address": invoice._get_address(invoice.partner_id),
                "doc_type": invoice.partner_id.l10n_latam_identification_type_id.name,
                "doc_nbr": invoice.partner_id.vat,
                "minigo_code": invoice.warehouse_id.code,
                "minigo_address": invoice._get_address(invoice.warehouse_id.partner_id),
                "origin": invoice.name,
                "date": inv_date,
                "time": inv_time,
                "seller": invoice.seller_id.vat,
                "amount_untaxed": invoice.amount_untaxed,
                "amount_tax": invoice.amount_tax,
                "amount_total": invoice.amount_total,
                "items": items
            }
            res.append(data)
        # payload = json.dumps(data)
        print(http.request.params)
        print(res)
        return res


class TestKey(http.Controller):
    @http.route('/test/key/', type='json', auth="user", methods=['POST'], cors="*", csrf=False)
    def test_api_key(self, **kw):
        print(http.request.params)
        res = {'AUTHORIZED': 200}
        return res

# 92c29b0ad3f13e8b02ddbfa13ed20bd8fe5dbba6
# curl -i -X POST -H "Content-Type: application/json" -d '{"params": {"id":22}}' 'https://g2f-api-rest.odoo.com/invoice/confirm/'