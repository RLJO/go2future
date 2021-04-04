# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from odoo.exceptions import ValidationError
from odoo import models, fields, api

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    type = fields.Selection(selection_add=[('product', 'Storable Product')],
                            tracking=True,
                            ondelete={'product': 'set default'},
                            default='product'
                            )
    brand = fields.Char(required=True)
    contents = fields.Integer(required=True)
    country_id = fields.Many2one('res.country',
                                 string='Origin Country',
                                 default=lambda self: self.env['res.country'].
                                 search([('code', 'ilike', 'AR')]),
                                 required=True)

    @api.constrains('contents')
    def _check_contents(self):
        for record in self:
            if record.contents <= 0:
                raise ValidationError('Contents cannot be <= 0')

    @api.constrains('barcode')
    def _check_length(self):
        for record in self:
            if len(record.barcode) > 13:
                raise ValidationError('Barcode length cannot be > 13')
