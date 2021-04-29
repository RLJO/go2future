# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class UoM(models.Model):
    _inherit = 'uom.uom'

    unit_for_sale = fields.Boolean(default=False)


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'
    _description = "Supplier Pricelist"

    warehouse_id = fields.Many2one('stock.warehouse', 'stock.warehouse',
                                   required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    type = fields.Selection(selection_add=[('product', 'Storable Product')],
                            tracking=True, track_visibility='always',
                            ondelete={'product': 'set default'},
                            default='product'
                            )
    brand = fields.Char(string='Brand', required=True, track_visibility='always')
    contents = fields.Integer('Contents', required=True, track_visibility='always')
    country_id = fields.Many2one('res.country',
                                 string='Origin Country',
                                 default=lambda self: self.env['res.country'].
                                 search([('code', 'ilike', 'AR')]),
                                 required=True, track_visibility='always')
    useful_life = fields.Integer(required=True, string='useful life in days',
                                 track_visibility='always')
    internal_tax = fields.Float('Internal Tax', required=True, digits=(16, 2),
                                default=0.0, track_visibility='always')
    units_per_package = fields.Integer('Units per Package', required=True,
                                       track_visibility='always')
    barcode = fields.Char(
        'Barcode', copy=False,
        size=13,
        help="EAN13 Number used for product identification.",
        track_visibility='always'
    )
    # list_price: catalog price, user defined
    list_price = fields.Float('Sales Price', default=1.0,
                              digits='Product Price',
                              help="Price at which the product is sold to customers.",
                              track_visibility='always')
    dun14 = fields.Char('Dun14', required=True, size=14, track_visibility='always')
    width = fields.Integer('Width', required=True, track_visibility='always')
    height = fields.Integer('Height', required=True, track_visibility='always')
    depth = fields.Integer('Depth', required=True, track_visibility='always')
    weight = fields.Integer('Weight', required=True, track_visibility='always')
    vegan = fields.Boolean('Vegan', default=False, track_visibility='always')
    organic = fields.Boolean('Organic', default=False,
                             track_visibility='always')
    without_tacc = fields.Boolean('Without Tac', default=False,
                                  track_visibility='always')
    sugar_free = fields.Boolean('Sugar Free', default=False,
                                track_visibility='always')
    optional_messages = fields.Text('Optional Messages', size=14,
                                    track_visibility='always')
    product_description = fields.Char('Product description', size=35,
                                      track_visibility='always')

    _sql_constraints = [(
        'product_template_dun14_uniq',
        'UNIQUE (dun14, active)',
        'Dun14 must be unique!'
    )]

    @api.constrains('contents')
    def _check_contents(self):
        for record in self:
            if record.contents <= 0:
                raise ValidationError(_('Contents cannot be <= 0'))

    @api.constrains('useful_life')
    def _check_length_useful_life(self):
        for record in self:
            if record.useful_life <= 0:
                raise ValidationError(_('Useful life length cannot be <=0'))

    @api.constrains('units_per_package')
    def _check_length_units_per_package(self):
        for record in self:
            if record.units_per_package <= 0 or \
                    len(str(record.units_per_package)) > 3:
                raise ValidationError(
                    _('Units per Package has be >0 and length char <= 3'))

    @api.constrains('dun14')
    def _check_length_dun14(self):
        for record in self:
            if len(record.dun14) != 14:
                raise ValidationError(_('Dun14 length has be = 14'))

    @api.constrains('barcode')
    def _check_length_barcode(self):
        for record in self:
            if len(record.barcode) != 13:
                raise ValidationError(_('Barcode length has be = 13'))

    @api.constrains('width')
    def _check_width(self):
        for record in self:
            if record.width <= 0:
                raise ValidationError(_('Width cannot be <= 0'))

    @api.constrains('height')
    def _check_height(self):
        for record in self:
            if record.height <= 0:
                raise ValidationError(_('Height cannot be <= 0'))

    @api.constrains('depth')
    def _check_depth(self):
        for record in self:
            if record.depth <= 0:
                raise ValidationError(_('depth cannot be <= 0'))

    @api.constrains('weight')
    def _check_weigth(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError(_('weight cannot be <= 0'))
