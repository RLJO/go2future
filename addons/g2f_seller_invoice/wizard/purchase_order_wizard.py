from odoo import models, fields, api, _
import datetime
import time
import zeep
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
            
            file_obj = self.env['ir.attachment'].search([('res_model', '=', 'purchase.order'),
                                                         ('res_id', '=', 2)])

            # file_content = base64.b64encode(bytes(data, 'utf-8'))
            file_content = file_obj.datas

            # https://api.planexware.net/PlanexwareWs
            # Ocp-Apim-Subscription-Key: 1381fbeede8243c6b87322169b623d8e
            # get_file = client.service.sendBill(filename + '.zip', base64.b64encode(str(data_file)))

            wsdlwsdlwsdlwsdlwsdl = '/home/boris/Descargas/PlanexwareWsWsdl'
            settings = zeep.Settings(extra_http_headers={
                'Ocp-Apim-Subscription-Key': '1381fbeede8243c6b87322169b623d8e'
            })
            function = 'ORDERS'
            file_name = 'file.txt'
            svc_url = 'https://api.planexware.net/PlanexwareWS'
            method_url = 'https://ws.planexware.net/PlanexwareWS/Upload'
            #
            function_header = zeep.xsd.Element('{http://test.python-zeep.org}Function', zeep.xsd.ComplexType([
                zeep.xsd.Element('{https://ws.planexware.net}Function', zeep.xsd.String())
            ]))
            filename_header = zeep.xsd.Element('{http://test.python-zeep.org}FileName', zeep.xsd.ComplexType([
                zeep.xsd.Element('{https://ws.planexware.net}FileName', zeep.xsd.String())
            ]))
            to_header = zeep.xsd.Element('{http://test.python-zeep.org}To', zeep.xsd.ComplexType([
                zeep.xsd.Element('{hhttp://schemas.microsoft.com/ws/2005/05/addressing/none}To', zeep.xsd.String())
            ]))
            action_header = zeep.xsd.Element('{http://test.python-zeep.org}Action', zeep.xsd.ComplexType([
                zeep.xsd.Element('{http://schemas.microsoft.com/ws/2005/05/addressing/none}Action', zeep.xsd.String())
            ]))
            # header_value = header(Function=function, FileName=file_name, Action=method_url, To=svc_url)

            # headers = {"Function": function, "FileName": file_name, "to": to, "action": action}
            function_header_value = function_header(Function=function)
            filename_header_value = filename_header(FileName=file_name)
            to_header_value = to_header(To=svc_url)
            action_header_value = action_header(Action=method_url)
            # header_value = {"Function": function, "FileName": file_name}

            # header = zeep.xsd.Element(None, zeep.xsd.ComplexType(
            #     zeep.xsd.Sequence([
            #         zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}Function', zeep.xsd.String()),
            #         zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}FileName', zeep.xsd.String()),
            #         zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}Action', zeep.xsd.String()),
            #         zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}To', zeep.xsd.String()),
            #     ])
            # ))

            header = zeep.xsd.Element(
                'customHeader',
                zeep.xsd.ComplexType([
                    zeep.xsd.Element('Function', zeep.xsd.String()),
                    zeep.xsd.Element('FileName', zeep.xsd.String()),
                    zeep.xsd.Element('Action', zeep.xsd.String()),
                    zeep.xsd.Element('To', zeep.xsd.String()),
                ])
            )
            #
            # PassengersType = xsd.ComplexType(
            #     xsd.Sequence([
            #         xsd.Element('passengers', PassengerType, min_occurs=1, max_occurs='unbounded')
            #     ]), qname=etree.QName("{http://example.com/schema}passengers")
            # )
            FunctionHeader = xsd.xsd.ComplexType(
                xsd.xsd.Sequence([
                    xsd.xsd.Element('function')
                ]), qname=etree.QName("{http://example.com/schema}function")
            )

            header_value = header(Function=function, FileName=file_name, Action=method_url, To=svc_url)
            upload_request = {"FileContent": file_content}

            # client = zeep.Client(wsdl=wsdl, settings=settings).service.GetStatus()
            try:
                client = zeep.Client(wsdl=wsdl, settings=settings).service.Upload(
                    file_content, _soapheaders=[header_value])
                print(client)
            except Fault as error:
                print(error.detail)

            # client = zeep.Client(wsdl=wsdl, settings=settings).service.Upload(
            #     _soapheaders=[
            #         filename_header_value,
            #         function_header_value,
            #         to_header_value,
            #         action_header_value
            #     ], UploadRequest=upload_request)
            #
            # client = zeep.Client(wsdl=wsdl, settings=settings).service.Upload(
            #     file_content,
            #     _soapheaders=[header_value])

            # b'SU5GTzAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwT1JERVJTXG5IRUFEMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwICAgIFAwMDAwMiAgICAgICAgICAgICAgICAgICAgICAgIENvbmNlcGNpw7NuIEFyZW5hbCAyOTQ3LCBDaXVkYWQgQXV0w7MgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAyMDIxMDcyNDIwMjEwNzI0ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDAwMDAwMDAwMDAwNy4yNjIwMjEwODAzMjIwNiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBQMDAwMDIgICAgICAgICAgICAgIFxuTElORTAwMDAwMTEyMTIxMjEyMTIxMjEgQ29jYSBDb2xhIFplcm8gICAgICAgICAgICAgICAgICAgICBDb2NhIENvbGEgWmVybyAgICAgICAgICAgICAgICAgICAgIDAwMDAwMDAwMDAwMDAwICAgICAgIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwICAgICAgICAgICAgICAgICAwMDAwMDAwMDAwMDAwLjYgICAgICAgICAgICAgICAwMDAwMDAwMDAwMDA2LjAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAoK'

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