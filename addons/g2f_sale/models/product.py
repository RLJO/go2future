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
    useful_life = fields.Integer(required=True, string='useful life in days')
    internal_tax = fields.Float(required=True, digits=(16, 2), default=0.0)
    units_per_package = fields.Integer(required=True)
    dun14 = fields.Char(required=True, size=14)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    depth = fields.Integer(required=True)
    weight = fields.Integer(required=True)

    _sql_constraints = [(
        'product_template_dun14_uniq',
        'UNIQUE (dun14, active)',
        'Dun14 must be unique!'
    )]

    @api.constrains('contents')
    def _check_contents(self):
        for record in self:
            if record.contents <= 0:
                raise ValidationError('Contents cannot be <= 0')

    @api.constrains('useful_life')
    def _check_length_useful_life(self):
        for record in self:
            if record.useful_life <= 0:
                raise ValidationError('Useful life length cannot be <=0')

    @api.constrains('units_per_package')
    def _check_length_units_per_package(self):
        for record in self:
            if record.units_per_package <= 0 or \
                    len(str(record.units_per_package)) > 3:
                raise ValidationError(
                    'Units per Package has be >0 and length char <= 3')

    @api.constrains('barcode')
    def _check_length(self):
        for record in self:
            if record.barcode and len(record.barcode) > 13:
                raise ValidationError('Barcode length cannot be > 13')

    @api.constrains('width')
    def _check_width(self):
        for record in self:
            if record.width <= 0:
                raise ValidationError('Width cannot be <= 0')

    @api.constrains('height')
    def _check_height(self):
        for record in self:
            if record.height <= 0:
                raise ValidationError('Height cannot be <= 0')

    @api.constrains('depth')
    def _check_depth(self):
        for record in self:
            if record.depth <= 0:
                raise ValidationError('depth cannot be <= 0')

    @api.constrains('weight')
    def _check_weigth(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError('weight cannot be <= 0')
