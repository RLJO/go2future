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
        if not kw.get('cuit'):
            return {'Error': 'No se recibio CUIT del vendedor'}
        res = []
        account = http.request.env['account.move']
        seller = http.request.env['res.partner']
        # seller_ids = seller.sudo().search([('vat', '=', kw.get('cuit').replace('-', ''))])
        seller_ids = seller.sudo().search([('vat', '=', kw.get('cuit'))])
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('seller_id', 'in', seller_ids.ids)
        ]
        if kw.get('start_date'):
            domain.append(('invoice_date', '>=', kw.get('start_date')))
        if kw.get('end_date'):
            domain.append(('invoice_date', '<=', kw.get('end_date')))

        moves = account.sudo().search(domain)
        for invoice in moves:
            items = []
            prisma = []
            # name = invoice.partner_id.name.split()
            # first_name = ''
            # last_name = ''
            # if len(name) == 2:
            #     first_name = name[0]
            #     last_name = name[1]
            # if len(name) >= 3:
            #     first_name = name[0] + ' ' + name[1]
            #     last_name = name[2]
            #     if len(name) == 4:
            #         last_name += ' ' + name[3]

            ('seller_api', _('API Seller')),
            ('afip', _('AFIP')),
            ('no_afip', _('No AFIP'))
            e_invoice_type = dict(invoice._fields['electronic_invoice_type'].selection).get(invoice.electronic_invoice_type)
            afip_auth_mode = invoice.l10n_ar_afip_auth_mode or ''
            afip_auth_code = invoice.l10n_ar_afip_auth_code or ''

            for line in invoice.invoice_line_ids:
                tax_items = []
                subtotal = line.price_unit * line.quantity
                for tax in line.tax_ids:
                    tax_amount = subtotal / (1 + tax.amount / 100)
                    tax_subtotal = subtotal - tax_amount
                    tax_item = {
                        "name": tax.name,
                        "amount": round(tax_subtotal, 2)
                    }
                    tax_items.append(tax_item)
                item = {
                    "EAN13": line.product_id.barcode,
                    "product": line.name,
                    "sku_code": line.product_id.default_code,
                    "quantity": line.quantity,
                    "unit_price": line.price_unit,
                    "discount": line.discount,
                    "tax": tax_items,
                    "subtotal": line.price_subtotal,
                    "amount_commission_plus_tax": line.amount_commission_plus_tax
                }
                items.append(item)

            for p in invoice.payment_prisma_status_ids:
                prisma = {
                    "transaction": p.site_transaction_id,
                    "card_brand": p.card_brand,
                    "card_type": p.card_type
                }

            data = {
                "id": invoice.id,
                "name": invoice.partner_id.name,
                "last_name": invoice.partner_id.lastname,
                "consumer_address": invoice._get_address(invoice.partner_id),
                "street": invoice.partner_id.street,
                "street2": invoice.partner_id.street2,
                "city": invoice.partner_id.city,
                "province": invoice.partner_id.state_id.name,
                "country": invoice.partner_id.country_id.name,
                "doc_type": invoice.partner_id.l10n_latam_identification_type_id.name,
                "doc_nbr": invoice.partner_id.vat,
                "minigo_code": invoice.warehouse_id.code,
                "minigo_address": invoice._get_address(invoice.warehouse_id.partner_id),
                "origin": invoice.name,
                "invoice_date": invoice.invoice_date,
                "invoice_type": invoice.l10n_latam_document_type_id.name,
                "seller": invoice.seller_id.vat,
                "amount_untaxed": invoice.amount_untaxed,
                "amount_tax": invoice.amount_tax,
                "amount_total": invoice.amount_total,
                "total_commission": invoice.total_commission,
                "total_less_commission": invoice.total_less_commission,
                "items": items,
                "number": invoice.invoice_origin,
                "afip_auth_code": afip_auth_mode + ' - ' + afip_auth_code if afip_auth_code else '',
                "afip_date_due": invoice.l10n_ar_afip_auth_code_due or '',
                "afip_result": invoice.l10n_ar_afip_result or '',
                "e_invoice_type": e_invoice_type,
                "prisma": prisma,
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