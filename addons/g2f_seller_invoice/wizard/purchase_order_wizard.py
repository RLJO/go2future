from odoo import models, fields, api, _
import datetime
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'
    _description = "Purchase Order Wizard"

    data = fields.Text('Data')

    def send_po(self):
        ids = self._context.get('active_ids')
        po_ids = self.env['purchase.order'].search([('id', 'in', ids)])
        send_date = time.strftime("%Y%m%d")
        send_time = time.strftime("%H%M")
        _logger.info("### Lista ### %r", po_ids.read())
        for po in po_ids:
            info = 'INFO'
            info += '0'.zfill(13)  # EAN del emisor
            info += '0'.zfill(13)  # EAN del Proveedor
            info += 'ORDERS'

            head = 'HEAD'
            head += '0'.zfill(13)  # EAN del emisor
            head += '0'.zfill(13)  # EAN del Proveedor
            head += '0'.zfill(13)  # EAN de la boca de entrega
            head += ''.ljust(4)
            head += po.name.ljust(10)
            head += ''.ljust(10)  # Código del proveedor
            head += ''.ljust(10)  # Descripción del Proveedor
            head += self._get_address(po.partner_id)[:35].ljust(10)
            head += ''.ljust(120)
            head += po.date_order.strftime('%Y%m%d') if po.date_order else ''
            head += po.date_planned.strftime('%Y%m%d') if po.date_planned else ''
            head += po.date_approve.strftime('%Y%m%d') if po.date_approve else ''
            head += ''.ljust(35)  # Forma de Pago / Observaciones
            head += ''.ljust(5)
            head += str(po.amount_total).zfill(15)
            head += send_date
            head += send_time
            head += ''.ljust(145)
            head += po.name.ljust(20)

            detail = 'LINE'
            detail += len(po.invoice_line_ids).zfill(6)
            for line in po.invoice_line_ids:
                detail += line.product_id.barcode.ljust(14)
                detail += line.name.ljust(35)
                detail += line.name.ljust(35)
                detail += line.product_id.default_code.zfill(14)
                detail += ''.ljust(7)
                detail += ''.zfill(7)  # Cantidad pedida en cajas (Package)
                detail += ''.zfill(11)  # Cantidad pedida en unidades
                detail += ''.zfill(5)  # Cantidad de unidades por package
                detail += ''.ljust(17)
                detail += line.price_unit.zfill(15)
                detail += ''.ljust(15)
                detail += line.price_subtotal.zfill(15)
                detail += ''.ljust(80)

            data = info + '\n' + head + '\n' + detail
            print(data)
            # https://api.planexware.net/PlanexwareWs
            # Ocp-Apim-Subscription-Key: 1381fbeede8243c6b87322169b623d8e
            # get_file = client.service.sendBill(filename + '.zip', base64.b64encode(str(data_file)))


    def _get_address(self, partner_id):
        address = partner_id.street + ', ' if partner_id.street else ''
        address += partner_id.street2 + ', ' if partner_id.street2 else ''
        address += partner_id.city + ', ' if partner_id.city else ''
        address += partner_id.state_id.name + ', ' if partner_id.state_id.name else ''
        address += 'CP: ' + partner_id.zip + ', ' if partner_id.zip else ''
        address += partner_id.country_id.name if partner_id.country_id.name else ''
        return address