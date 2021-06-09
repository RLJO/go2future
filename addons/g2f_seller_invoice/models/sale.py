# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import time
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        inv_id = super(SaleOrder, self)._create_invoices(grouped=False, final=False, date=None)
        if inv_id:
            invoice = self.env['account.move'].browse([inv_id])
            items = []
            date_order = str(invoice.invoice_date).split() if invoice.invoice_date else ''
            consumer_address = invoice.partner_id.street + ', ' if invoice.partner_id.street else ''
            consumer_address += invoice.partner_id.street2 + ', ' if invoice.partner_id.street2 else ''
            consumer_address += invoice.partner_id.city + ', ' if invoice.partner_id.city else ''
            consumer_address += invoice.partner_id.state_id.name + ', ' if invoice.partner_id.state_id.name else ''
            consumer_address += 'CP: ' + invoice.partner_id.zip + ', ' if invoice.partner_id.zip else ''
            consumer_address += invoice.partner_id.country_id.name if invoice.partner_id.country_id.name else ''

            for line in invoice.invoice_line_ids:
                product = line.name
                barcode = line.product_id.barcode
                quantity = line.product_uom_qty
                unit_price = line.price_unit
                subtotal = line.price_subtotal
                api_path = line.seller.api_path
                item = {
                    "EAN13": barcode,
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal
                }
                items.append(item)

            data = {
                "id": self.id,
                "name": self.partner_id.name,
                "last_name": self.partner_id.name,
                "consumer_address": consumer_address,
                "dni": self.partner_id.vat,
                "minigo_address": "Av. San Martin, Ciudad: Buenos Aires, CP: 1444, País: Argentina",
                "date": date_order[0],
                "time": date_order[1],
                "items": items
            }

            # url = seller_id.api_path  # "http://dummy.minigo.store/orders"
            # token = company_id.api_token
            payload = json.dumps(data)
            headers = {
                'Content-Type': "application/json",
                # 'Authorization': token,  # "Bearer WwfnXumP22Oknu80TyoifcWafS7RTWJSrPlGeFCM9D5pNfWcry",
                'Cache-Control': "no-cache",
            }
            try:
                response = requests.request("POST", api_path, data=payload, headers=headers)
            except Exception as exc:
                raise UserError(_("Error inesperado %s") % exc)

            print(response.text)
            print(payload)
            _logger.warning('Json enviado: (%s).', payload)

    def action_confirm_old(self):
        self.ensure_one()
        res = super(SaleOrder, self).action_confirm()
        if res:
            items = []
            date_order = str(self.date_order).split() if self.date_order else ''
            consumer_address = self.partner_id.street + ', ' if self.partner_id.street else ''
            consumer_address += self.partner_id.street2 + ', ' if self.partner_id.street2 else ''
            consumer_address += self.partner_id.city + ', ' if self.partner_id.city else ''
            consumer_address += self.partner_id.state_id.name + ', ' if self.partner_id.state_id.name else ''
            consumer_address += 'CP: ' + self.partner_id.zip + ', ' if self.partner_id.zip else ''
            consumer_address += self.partner_id.country_id.name if self.partner_id.country_id.name else ''

            for line in self.order_line:
                product = line.name
                barcode = line.product_id.barcode
                quantity = line.product_uom_qty
                unit_price = line.price_unit
                subtotal = line.price_subtotal
                item = {
                    "EAN13": barcode,
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal
                }
                items.append(item)

            data = {
                "id": self.id,
                "name": self.partner_id.name,
                "last_name": self.partner_id.name,
                "consumer_address": consumer_address,
                "dni": self.partner_id.vat,
                "minigo_address": "Av. San Martin, Ciudad: Buenos Aires, CP: 1444, País: Argentina",
                "date": date_order[0],
                "time": date_order[1],
                "items": items
            }

            url = self.marketplace_seller_id.api_path  # "http://dummy.minigo.store/orders"
            # token = company_id.api_token
            payload = json.dumps(data)
            headers = {
                'Content-Type': "application/json",
                # 'Authorization': token,  # "Bearer WwfnXumP22Oknu80TyoifcWafS7RTWJSrPlGeFCM9D5pNfWcry",
                'Cache-Control': "no-cache",
            }
            try:
                response = requests.request("POST", url, data=payload, headers=headers)
            except Exception as exc:
                raise UserError(_("Error inesperado %s") % exc)

            print(response.text)
            print(payload)
            _logger.warning('Json enviado: (%s).', payload)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def confirmar_orden(self, vals):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('id', '=', vals['id']), ('invoice_status', '!=', 'invoiced')])
        res = 'No se encontró una orden registrada con el id: %s' % vals['id']
        if order_id:
            sale_orders = self.env['sale.order'].browse(order_id.id)
            res = sale_orders._create_invoices(final=True)
            res.write({
                'einvoice': vals['einvoice'],
                'date_einvoice': vals['date_einvoice'],
                'cae_number': vals['cae_number'],
                'ei_qr_code': vals['ei_qr_code'],
                'ei_barcode': vals['ei_barcode'],
                'ei_xml_file': vals['ei_xml_file'],
                'ei_pdf': vals['ei_pdf']
            })
            # with open("/home/boris/Descargas/frame.png", "rb") as f:
            #     encodedZip = base64.b64encode(f.read())
            #     print(encodedZip.decode())

            # if res: order_id.write({'invoice_status': 'invoiced'})
        return res