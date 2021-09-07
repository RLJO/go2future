# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from OpenSSL import crypto

import base64
import logging
import random
import re

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    electronic_invoice_type = fields.Selection(selection=[
        ('seller_api', _('API Seller')),
        ('afip', _('AFIP')),
        ('no_afip', _('No AFIP'))
    ], string=_('Invoicing Type'), default='afip')
    l10n_ar_connection_ids = fields.One2many('l10n_ar.afipws.connection', 'partner_id', 'Connections')
    l10n_ar_afip_ws_environment = fields.Selection([('testing', _('Testing')), ('production', _('Production'))],
                                                   string=_("AFIP Environment"), default='production')
    l10n_ar_afip_ws_key_fname = fields.Char(string=_('Private Key'), default='private_key.pem')
    l10n_ar_afip_ws_key = fields.Binary(string=_('Private Key'), attachment=True)
    l10n_ar_afip_ws_crt_fname = fields.Char(string=_('Certificate'), compute="_compute_l10n_ar_afip_ws_crt_fname", store=True)
    l10n_ar_afip_ws_crt = fields.Binary(string=_('Private Key'), attachment=True)
    fe_journal_id = fields.Many2one(comodel_name='account.journal', string=_('Diario'), domain='[("type", "=", "sale")]')
    invoice_type_cae_caea = fields.Selection(selection=[
        ('cae', _('CAE')),
        ('caea', _('CAEA')),
    ], string=_('Invoicing Type'), default='cae')
    account_move_line_caea_ids = fields.One2many('account.move.caea.line', 'res_partner_id', string=_('Datos CAEA'), track_visibility='onchange')
    full_direction = fields.Char(_('Domicilio legal completo'))
    customer_attention_phone = fields.Char(_('Teléfono de atención al cliente'))
    customer_attention_email = fields.Char(_('Email de atención al cliente'))
    customer_attention_website = fields.Char(_('Website de atención al cliente'))
    cuit_an = fields.Boolean('C.U.I.T/A.N. Se.S N°?', default=False)

    def l10n_ar_connection_test(self):
        self.ensure_one()
        error = ''
        if not self.l10n_ar_afip_ws_crt:
            error += '\n* ' + _('Please set a certificate in order to make the test')
        if not self.l10n_ar_afip_ws_key:
            error += '\n* ' + _('Please set a private key in order to make the test')
        if error:
            raise UserError(error)

        res = ''
        for webservice in ['wsfe', 'wsfex', 'wsbfe', 'wscdc']:
            try:
                self._l10n_ar_get_connection(webservice)
                res += ('\n* %s: ' + _('Connection is available')) % webservice
            except UserError as error:
                hint_msg = re.search('.*(HINT|CONSEJO): (.*)', error.name)
                msg = hint_msg.groups()[-1] if hint_msg and len(hint_msg.groups()) > 1 \
                    else '\n'.join(re.search('.*' + webservice + ': (.*)\n\n', error.name).groups())
                res += '\n* %s: ' % webservice + _('Connection failed') + '. %s' % msg.strip()
            except Exception as error:
                res += ('\n* %s: ' + _('Connection failed') + '. ' + _('This is what we get') + ' %s') % (webservice, repr(error))
        raise UserError(res)

    @api.depends('l10n_ar_afip_ws_crt')
    def _compute_l10n_ar_afip_ws_crt_fname(self):
        with_crt = self.filtered(lambda x: x.l10n_ar_afip_ws_crt)
        remaining = self - with_crt
        for rec in with_crt:
            certificate = self._l10n_ar_get_certificate_object(rec.l10n_ar_afip_ws_crt)
            rec.l10n_ar_afip_ws_crt_fname = certificate.get_subject().CN
        remaining.l10n_ar_afip_ws_crt_fname = ''

    def l10n_ar_action_create_certificate_request(self):
        self.ensure_one()
        if not self.city:
            raise UserError(_('The company city must be defined before this action'))
        if not self.country_id:
            raise UserError(_('The company country must be defined before this action'))
        if not self.l10n_ar_vat:
            raise UserError(_('The company CUIT must be defined before this action'))
        return {'type': 'ir.actions.act_url', 'url': '/l10n_ar_edi/download_partner_csr/' + str(self.id), 'target': 'new'}

    @api.constrains('l10n_ar_afip_ws_crt')
    def _l10n_ar_check_afip_certificate(self):
        for rec in self.filtered('l10n_ar_afip_ws_crt'):
            error = False
            try:
                content = base64.decodebytes(rec.l10n_ar_afip_ws_crt).decode('ascii')
                crypto.load_certificate(crypto.FILETYPE_PEM, content)
            except Exception as exc:
                if 'Expecting: CERTIFICATE' in repr(exc) or "('PEM routines', 'get_name', 'no start line')" in repr(exc):
                    error = _('Wrong certificate file format.\nPlease upload a valid PEM certificate.')
                else:
                    error = _('Not a valid certificate file')
                _logger.warning('%s %s' % (error, repr(exc)))
            if error:
                raise ValidationError('\n'.join([_('The certificate can not be uploaded!'), error]))

    @api.constrains('l10n_ar_afip_ws_key')
    def _l10n_ar_check_afip_private_key(self):
        for rec in self.filtered('l10n_ar_afip_ws_key'):
            error = False
            try:
                content = base64.decodebytes(rec.l10n_ar_afip_ws_key).decode('ascii').strip()
                crypto.load_privatekey(crypto.FILETYPE_PEM, content)
            except Exception as exc:
                error = _('Not a valid private key file')
                _logger.warning('%s %s' % (error, repr(exc)))
            if error:
                raise ValidationError('\n'.join([_('The private key can not be uploaded!'), error]))

    def _l10n_ar_get_certificate_object(self, cert):
        crt_str = base64.decodebytes(cert).decode('ascii')
        res = crypto.load_certificate(crypto.FILETYPE_PEM, crt_str)
        return res

    def _l10n_ar_get_afip_crt_expire_date(self):
        self.ensure_one()
        crt = self.l10n_ar_afip_ws_crt
        if crt:
            certificate = self._l10n_ar_get_certificate_object(crt)
            datestring = certificate.get_notAfter().decode()
            return datetime.strptime(datestring, '%Y%m%d%H%M%SZ').date()

    def _l10n_ar_is_afip_crt_expire(self):
        self.ensure_one()
        expire_date = self._l10n_ar_get_afip_crt_expire_date()
        if expire_date and expire_date < fields.Date.today():
            raise UserError(_('The AFIP certificate is expired, please renew in order to continue'))

    def _get_environment_type(self):
        self.ensure_one()
        if not self.l10n_ar_afip_ws_environment:
            raise UserError(_('AFIP environment not configured for seller "%s", please check settings') % (self.name))
        return self.l10n_ar_afip_ws_environment

    def _l10n_ar_get_connection(self, afip_ws):
        self.ensure_one()
        if not afip_ws:
            raise UserError(_('No AFIP WS selected'))

        env_type = self._get_environment_type()
        connection = self.l10n_ar_connection_ids.search([('type', '=', env_type), ('l10n_ar_afip_ws', '=', afip_ws), ('partner_id', '=', self.id)], limit=1)

        if connection and connection.expiration_time > fields.Datetime.now():
            return connection

        token_data = connection._l10n_ar_get_token_data(False, afip_ws, self)
        if connection:
            connection.sudo().write(token_data)
        else:
            values = {'partner_id': self.id, 'l10n_ar_afip_ws': afip_ws, 'type': env_type}
            values.update(token_data)
            _logger.info('Connection created for seller %s %s (%s)' % (self.name, afip_ws, env_type))
            connection = connection.sudo().create(values)

        if not self.env.context.get('l10n_ar_invoice_skip_commit'):
            self._cr.commit()
        _logger.info("Successful Authenticated with AFIP.")

        return connection

    def _get_key_and_certificate(self):
        self.ensure_one()
        pkey = base64.decodebytes(self.l10n_ar_afip_ws_key) if self.l10n_ar_afip_ws_key else ''
        cert = base64.decodebytes(self.l10n_ar_afip_ws_crt) if self.l10n_ar_afip_ws_crt else ''
        res = (pkey, cert)
        if not all(res):
            error = '\n * ' + _(' Missing private key.') if not pkey else ''
            error += '\n * ' + _(' Missing certificate.') if not cert else ''
            raise UserError(_('Missing configuration to connect to AFIP:') + error)
        self._l10n_ar_is_afip_crt_expire()
        return res

    def _generate_afip_private_key(self, key_length=2048):
        for rec in self:
            key_obj = crypto.PKey()
            key_obj.generate_key(crypto.TYPE_RSA, key_length)
            key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_obj)
            key = base64.b64encode(key)
            rec.l10n_ar_afip_ws_key = key

    def _l10n_ar_create_certificate_request(self):
        self.ensure_one()
        req = crypto.X509Req()
        req_subject = req.get_subject()
        req_subject.C = self.country_id.code.encode('ascii', 'ignore')

        if self.state_id:
            req_subject.ST = self.state_id.name.encode('ascii', 'ignore')

        common_name = 'AFIP WS %s - %s' % (self._get_environment_type(), self.name)
        common_name = common_name[:50]

        req_subject.L = self.city.encode('ascii', 'ignore')
        req_subject.O = self.name.encode('ascii', 'ignore')
        req_subject.OU = 'IT'.encode('ascii', 'ignore')
        req_subject.CN = common_name.encode('ascii', 'ignore')
        req_subject.serialNumber = ('CUIT %s' % self.ensure_vat()).encode('ascii', 'ignore')

        if not self.l10n_ar_afip_ws_key:
            self._generate_afip_private_key()
        pkey = base64.decodebytes(self.l10n_ar_afip_ws_key)

        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, pkey)
        req.set_pubkey(private_key)
        req.sign(private_key, 'sha256')
        csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
        return csr

    def set_demo_random_cert(self):
        for rec in self:
            old = rec.l10n_ar_afip_ws_crt_fname
            cert_file = get_module_resource('l10n_ar_edi', 'demo', 'cert%d.crt' % random.randint(1, 10))
            rec.l10n_ar_afip_ws_crt = base64.b64encode(open(cert_file, 'rb').read())
            _logger.log(25, 'Setting demo certificate from %s to %s in seller %s' % (
            old, rec.l10n_ar_afip_ws_crt_fname, rec.name))

    def get_last_caea_record(self):
        if len(self.account_move_line_caea_ids):
            records = self.account_move_line_caea_ids.sorted(key=lambda r: r.caea_creation_date, reverse=True)
            for record in records:
                return record
            return False

class AccountMoveCaeaLine(models.Model):
    _name = 'account.move.caea.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    res_partner_id = fields.Many2one('res.partner')
    caea_creation_date = fields.Datetime(_('Fecha de creación'), default=lambda self: fields.datetime.now(),readonly=True, store=True, track_visibility="onchange")
    caea_validity_from = fields.Date(_('Vigencia desde'), required=True, track_visibility="onchange")
    caea_validity_to = fields.Date(_('Vigencia hasta'), required=True, track_visibility="onchange")
    caea_number = fields.Char(_('CAEA N°'), required=True, track_visibility="onchange")
