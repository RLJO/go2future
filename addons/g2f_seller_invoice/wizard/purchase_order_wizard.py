from odoo import models, fields, api, _
import datetime
import time
from zeep import Client, xsd
from zeep.exceptions import Fault
import base64
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
            info += '9500000598565'.zfill(13)  # EAN del emisor
            info += '7792900000008'.zfill(13)  # EAN del Proveedor
            info += 'ORDERS'

            head = 'HEAD'
            head += '9500000598565'.zfill(13)  # EAN del emisor
            head += '7792900000008'.zfill(13)  # EAN del Proveedor
            head += '9500000598565'.zfill(13)  # EAN de la boca de entrega
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
            detail += str(len(po.order_line)).zfill(6)
            for line in po.order_line:
                default_code = line.product_id.default_code or ''
                detail += line.product_id.barcode.ljust(14)
                detail += line.name.ljust(35)
                detail += line.name.ljust(35)
                detail += default_code.zfill(14)
                detail += ''.ljust(7)
                detail += ''.zfill(7)  # Cantidad pedida en cajas (Package)
                detail += ''.zfill(11)  # Cantidad pedida en unidades
                detail += ''.zfill(5)  # Cantidad de unidades por package
                detail += ''.ljust(17)
                detail += str(line.price_unit).zfill(15)
                detail += ''.ljust(15)
                detail += str(line.price_subtotal).zfill(15)
                detail += ''.ljust(80)

            data = info + '\n' + head + '\n' + detail
            print(data)
            
            file_obj = self.env['ir.attachment'].search([('res_model', '=', 'purchase.order'), ('res_id', '=', 2)])

            # file_content = base64.b64encode(bytes(data, 'utf-8'))
            file_content = file_obj.datas

            # https://api.planexware.net/PlanexwareWs
            # Ocp-Apim-Subscription-Key: 1381fbeede8243c6b87322169b623d8e
            # get_file = client.service.sendBill(filename + '.zip', base64.b64encode(str(data_file)))

            wsdl = '/home/boris/Descargas/PlanexwareWsWsdl'
            # settings = zeep.Settings(extra_http_headers={
            #     'Ocp-Apim-Subscription-Key': '1381fbeede8243c6b87322169b623d8e',
            #     'Company': 'GO2FUTURE'
            # })

            client = Client(wsdl)

            settings = {
                'Ocp-Apim-Subscription-Key': '1381fbeede8243c6b87322169b623d8e',
                'Company': 'GO2FUTURE'
            }
            client.settings.extra_http_headers = settings

            function = 'ORDERS'
            file_name = 'file.txt'

            # b'SU5GTzAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwT1JERVJTXG5IRUFEMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwICAgIFAwMDAwMiAgICAgICAgICAgICAgICAgICAgICAgIENvbmNlcGNpw7NuIEFyZW5hbCAyOTQ3LCBDaXVkYWQgQXV0w7MgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAyMDIxMDcyNDIwMjEwNzI0ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDAwMDAwMDAwMDAwNy4yNjIwMjEwODAzMjIwNiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBQMDAwMDIgICAgICAgICAgICAgIFxuTElORTAwMDAwMTEyMTIxMjEyMTIxMjEgQ29jYSBDb2xhIFplcm8gICAgICAgICAgICAgICAgICAgICBDb2NhIENvbGEgWmVybyAgICAgICAgICAgICAgICAgICAgIDAwMDAwMDAwMDAwMDAwICAgICAgIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwICAgICAgICAgICAgICAgICAwMDAwMDAwMDAwMDAwLjYgICAgICAgICAgICAgICAwMDAwMDAwMDAwMDA2LjAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAoK'

            header = xsd.ComplexType(
                xsd.Sequence([
                    xsd.Element('Function', xsd.String()),
                    xsd.Element('FileName', xsd.String()),
                ])
            )
            headers = [header(Function=function, FileName=file_name)]
            client.set_default_soapheaders(headers)

            client.service.Upload(file_content)


            xml = """
                <?xml version=”1.0”?>
                <s:Envelope xmlns:s=”http://schemas.xmlsoap.org/soap/envelope/”>
                    <s:Header>
                    <Function xmlns=”https://ws.planexware.net”>ORDERS</Function>
                    <FileName xmlns=”https://ws.planexware.net”>ORD_1111222710006_3334445300149978_77980327199999.txt</FileName>
                    <To s:mustUnderstand=”1” xmlns=”http://schemas.microsoft.com/ws/2005/05/addressing/none”>
                    https://api.planexware.net/PlanexwareWS </To>
                    <Action s:mustUnderstand=”1” xmlns=”http://schemas.microsoft.com/ws/2005/05/addressing/none”>
                https://ws.planexware.net/PlanexwareWS/Upload</Action>
                </s:Header>
                <s:Body>
                <UploadRequest xmlns=”https://ws.planexware.net”>
                <FileContent>%r</FileContent>
                </UploadRequest>
                </s:Body>
                </s:Envelope>
            """ % file_content







    def _get_address(self, partner_id):
        address = partner_id.street + ', ' if partner_id.street else ''
        address += partner_id.street2 + ', ' if partner_id.street2 else ''
        address += partner_id.city + ', ' if partner_id.city else ''
        address += partner_id.state_id.name + ', ' if partner_id.state_id.name else ''
        address += 'CP: ' + partner_id.zip + ', ' if partner_id.zip else ''
        address += partner_id.country_id.name if partner_id.country_id.name else ''
        return address