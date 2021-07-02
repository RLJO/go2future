# -*- coding: utf-8 -*-

from lxml import builder, etree
from odoo import fields, models
from OpenSSL import crypto

import base64
import datetime
import logging
import time
import zeep

_logger = logging.getLogger(__name__)

class ARTransport(zeep.transports.Transport):
    def post(self, address, message, headers):
        response = super().post(address, message, headers)
        self.xml_request = etree.tostring(
            etree.fromstring(message), pretty_print=True).decode('utf-8')
        self.xml_response = etree.tostring(
            etree.fromstring(response.content), pretty_print=True).decode('utf-8')
        return response

class L10nArAfipwsConnection(models.Model):
    _inherit = "l10n_ar.afipws.connection"

    company_id = fields.Many2one('res.company', index=True, auto_join=True, required=False)
    partner_id = fields.Many2one('res.partner', index=True, auto_join=True)

    def _get_client(self, return_transport=False):
        """ Get zeep client to connect to the webservice """
        wsdl = self._l10n_ar_get_afip_ws_url(self.l10n_ar_afip_ws, self.type)
        if self.partner_id:
            auth = {'Token': self.token, 'Sign': self.sign, 'Cuit': self.partner_id.ensure_vat()}
        else:
            auth = {'Token': self.token, 'Sign': self.sign, 'Cuit': self.company_id.partner_id.ensure_vat()}
        try:
            transport = ARTransport(operation_timeout=60, timeout=60)
            client = zeep.Client(wsdl, transport=transport)
        except Exception as error:
            self._l10n_ar_process_connection_error(error, self.type, self.l10n_ar_afip_ws)
        if return_transport:
            return client, auth, transport
        return client, auth

    def _l10n_ar_get_token_data(self, company, afip_ws, partner=False):
        if partner:
            private_key, certificate = partner.sudo()._get_key_and_certificate()
            environment_type = partner._get_environment_type()
        else:
            private_key, certificate = company.sudo()._get_key_and_certificate()
            environment_type = company._get_environment_type()
        generation_time = fields.Datetime.now()
        expiration_time = fields.Datetime.add(generation_time, hours=12)
        uniqueId = str(int(time.mktime(datetime.datetime.now().timetuple())))
        request_xml = (builder.E.loginTicketRequest({
            'version': '1.0'},
            builder.E.header(builder.E.uniqueId(uniqueId),
                             builder.E.generationTime(generation_time.strftime('%Y-%m-%dT%H:%M:%S-00:00')),
                             builder.E.expirationTime(expiration_time.strftime('%Y-%m-%dT%H:%M:%S-00:00'))),
            builder.E.service(afip_ws)))
        request = etree.tostring(request_xml, pretty_print=True)

        # sign request
        PKCS7_NOSIGS = 0x4
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
        signcert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        bio_in = crypto._new_mem_buf(request)
        pkcs7 = crypto._lib.PKCS7_sign(signcert._x509, pkey._pkey, crypto._ffi.NULL, bio_in, PKCS7_NOSIGS)
        bio_out = crypto._new_mem_buf()
        crypto._lib.i2d_PKCS7_bio(bio_out, pkcs7)
        signed_request = crypto._bio_to_string(bio_out)

        wsdl = {'production': "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL",
                'testing': "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL"}.get(environment_type)

        try:
            if partner:
                _logger.info('Connect to AFIP to get token: %s %s %s' % (afip_ws, partner.l10n_ar_afip_ws_crt_fname, partner.name))
            else:
                _logger.info('Connect to AFIP to get token: %s %s %s' % (afip_ws, company.l10n_ar_afip_ws_crt_fname, company.name))
            transport = ARTransport(operation_timeout=60, timeout=60)
            client = zeep.Client(wsdl, transport=transport)
            response = client.service.loginCms(base64.b64encode(signed_request).decode())
        except Exception as error:
            return self._l10n_ar_process_connection_error(error, environment_type, afip_ws)
        response = etree.fromstring(response.encode('utf-8'))

        return {'uniqueid': uniqueId,
                'generation_time': generation_time,
                'expiration_time': expiration_time,
                'token': response.xpath('/loginTicketResponse/credentials/token')[0].text,
                'sign': response.xpath('/loginTicketResponse/credentials/sign')[0].text}