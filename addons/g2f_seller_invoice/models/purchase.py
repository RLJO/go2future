# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    pw_status_code = fields.Integer('PlanexWare Status Code')
    pw_xml_response = fields.Text('PlanexWare XML Response')
    pw_plane_text = fields.Text('Krikos Plane Text')
