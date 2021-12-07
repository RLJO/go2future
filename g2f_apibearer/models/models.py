# -*- coding: utf-8 -*-
import binascii
import logging
import os
import time
from collections import defaultdict
from hashlib import sha256
from itertools import chain, repeat
import passlib
from werkzeug.exceptions import BadRequest

from odoo.addons.base.models.res_users import check_identity
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# API keys support
API_KEY_SIZE = 60 # in bytes
INDEX_SIZE = 8 # in hex digits, so 4 bytes, or 20% of the key
KEY_CRYPT_CONTEXT = passlib.context.CryptContext(
    # default is 29000 rounds which is 25~50ms, which is probably unnecessary
    # given in this case all the keys are completely random data: dictionary
    # attacks on API keys isn't much of a concern
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)
hash_api_bkey = getattr(KEY_CRYPT_CONTEXT, 'hash', None) or KEY_CRYPT_CONTEXT.encrypt

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_api_key(cls):
        api_key = request.httprequest.headers.get("Authorization")
        if not api_key:
            raise BadRequest("Authorization header with API key missing")

        # user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        if api_key != 'Bearer APIHOLA1234':
            raise BadRequest("API key invalid")
        #request.uid = user_id


class AppTokens(models.Model):
    _name = 'Token by Application'
    _description = 'App Tokens'

    name = fields.Char(string="Application")
    bearertoken = fields.Char(string="API Token")
    exp_date = fields.Datetime(string="Expiration date")

    def _check_credentials(self, *, scope, key):
        assert scope, "scope is required"
        index = key[:INDEX_SIZE]
        self.env.cr.execute('''
            SELECT user_id, key
            FROM res_users_apikeys INNER JOIN res_users u ON (u.id = user_id)
            WHERE u.active and index = %s AND (scope IS NULL OR scope = %s)
        ''', [index, scope])
        for user_id, current_key in self.env.cr.fetchall():
            if KEY_CRYPT_CONTEXT.verify(key, current_key):
                return user_id

    def _generate(self, scope, name):
        """Generates an api key.
        :param str scope: the scope of the key. If None, the key will give access to any rpc.
        :param str name: the name of the key, mainly intended to be displayed in the UI.
        :return: str: the key.

        """
        # no need to clear the LRU when *adding* a key, only when removing
        k = binascii.hexlify(os.urandom(API_KEY_SIZE)).decode()
        self.env.cr.execute("""
        INSERT INTO res_users_apikeys (name, user_id, scope, key, index)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        [name, self.env.user.id, scope, hash_api_bkey(k), k[:INDEX_SIZE]])

        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info("API key generated: scope: <%s> for '%s' (#%s) from %s",
            scope, self.env.user.login, self.env.uid, ip)

        return k

    @check_identity
    def make_key(self):
        # only create keys for users who can delete their keys
        if not self.user_has_groups('base.group_user'):
            raise AccessError(_("Only internal users can create API keys"))

        description = self.sudo()
        k = self.env['res.users.apikeys']._generate(None, self.sudo().name)
        description.unlink()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.users.apikeys.show',
            'name': 'API Key Ready',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_key': k,
            }
        }