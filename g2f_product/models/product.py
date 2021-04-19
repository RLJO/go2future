# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sector = fields.Many2one('product.sector', 'Sector', required=True)
    familia = fields.Many2one('product.familia', 'Family', required=True)
    subfamilia = fields.Many2one('product.subfamilia', 'Subfamily', required=True)
    categoria = fields.Many2one('product.categoria', 'Category', required=True)
    alto = fields.Integer('Height (mm)', required=True)
    ancho = fields.Integer('Width (mm)', required=True)
    profundidad = fields.Integer('Depth (mm)', required=True)
    peso_bruto = fields.Integer('Gross weight (g)', required=True)
    layout = fields.Selection(selection=[('D', 'Dry'), ('C', 'Cold'), ('F', 'Frozen')], required=True)
    cant_frente = fields.Integer('Number of units per front', required=True)
    cant_fondo = fields.Integer('Number of units per fund', required=True)
    cant_altura = fields.Integer('Number of units per height', required=True)
    gondola = fields.Char('Gondola position', required=True, size=14)
    peso_estante = fields.Integer('Total weight of the shelf', compute='_get_peso_estante')
    aptitud = fields.Integer('Lifetime fitness percentage', required=True, default=70)
    desc_tag = fields.Char('TAG short description', required=True)
    atributos_ids = fields.Many2many('product.atributos', 'product_atributos_rel', 'prod_id', 'atributos_id', string='Attributes')
    product_label = fields.Text('Product Label', compute='_get_label')

    @api.depends('peso_bruto', 'cant_frente', 'cant_fondo', 'cant_altura')
    def _get_peso_estante(self):
        self.peso_estante = self.peso_bruto * self.cant_frente * self.cant_fondo * self.cant_altura

    @api.onchange('sector')
    def onchange_sector(self):
        res = {}
        familia_obj = self.env['product.familia']
        familia_ids = familia_obj.search([('sector', '=', self.sector.id)])
        if familia_ids:
            res['domain'] = {'familia': [('id', 'in', familia_ids.ids)]}
        else:
            res['domain'] = {'familia': [('id', '=', 0)]}
        self.familia = False
        return res

    @api.onchange('familia')
    def onchange_familia(self):
        res = {}
        subfamilia_obj = self.env['product.subfamilia']
        subfamilia_ids = subfamilia_obj.search([('familia', '=', self.familia.id)])
        if subfamilia_ids:
            res['domain'] = {'subfamilia': [('id', 'in', subfamilia_ids.ids)]}
        else:
            res['domain'] = {'subfamilia': [('id', '=', 0)]}
        self.subfamilia = False
        return res

    @api.onchange('subfamilia')
    def onchange_subfamilia(self):
        res = {}
        categoria_obj = self.env['product.categoria']
        categoria_ids = categoria_obj.search([('subfamilia', '=', self.subfamilia.id)])
        if categoria_ids:
            res['domain'] = {'categoria': [('id', 'in', categoria_ids.ids)]}
        else:
            res['domain'] = {'categoria': [('id', '=', 0)]}
        self.categoria = False
        return res

    def write(self, vals):
        if 'gondola' in vals and len(vals['gondola']) != 14:
            raise UserError(_('The field (Position in gondola: %s) must contain 14 characters', vals['gondola']))
        if 'cant_frente' in vals and int(vals['cant_frente']) == 0:
            raise UserError(_('The field (Number of units per front: %s) must be greater than zero',
                              vals['cant_frente']))
        if 'cant_fondo' in vals and int(vals['cant_fondo']) == 0:
            raise UserError(_('The field (Number of units per fund: %s) must be greater than zero',
                              vals['cant_fondo']))
        if 'cant_altura' in vals and int(vals['cant_altura']) == 0:
            raise UserError(_('The field (Number of units per height: %s) must be greater than zero',
                              vals['cant_altura']))
        return super(ProductTemplate, self).write(vals)

    @api.depends('list_price', 'desc_tag', 'uom_id')
    def _get_label(self):
        if self.list_price == 0:
            raise UserError(_('The Sale Price must be greater than zero (0)'))
        if self.uom_id.name == 'Unidades':
            uom_price = 'Und ' + str(self.list_price)
        else:
            uom_price = self._get_uom_price(self.uom_id, self.list_price)

        label = str(self.env.user.company_id.currency_id.symbol)
        label += str(self.list_price) + '\n'
        label += str(self.desc_tag) + '\n'
        label += str(self.uom_id.name) + '\n'
        label += 'Precio por cada ' + uom_price
        self.product_label = label

    def _get_uom_price(self, uom, price):
        ref_unid = self.env['uom.uom'].search([('category_id', '=', uom.category_id.id),
                                               ('uom_type', '=', 'reference')])
        if uom.uom_type == 'bigger':
            uom_price = uom.factor_inv / price
        elif uom.uom_type == 'smaller':
            uom_price = uom.factor_inv * price
        return ref_unid.name + ' ' + str(uom_price)


class ProductSector(models.Model):
    _name = 'product.sector'
    _description = 'Sector'

    nro = fields.Integer('Sector Nbr.')
    name = fields.Char('Sector')


class ProductFamilia(models.Model):
    _name = 'product.familia'
    _description = 'Familia'

    nro = fields.Integer('Family Nbr.')
    name = fields.Char('Family')
    sector = fields.Many2one('product.sector', 'Sector')


class ProductSubfamilia(models.Model):
    _name = 'product.subfamilia'
    _description = 'Subfamilia'

    nro = fields.Integer('Subfamily Nbr.')
    name = fields.Char('Subfamily')
    familia = fields.Many2one('product.familia', 'Family')


class ProductCategoria(models.Model):
    _name = 'product.categoria'
    _description = 'Categoria'

    nro = fields.Integer('Category Nbr.')
    name = fields.Char('Category')
    subfamilia = fields.Many2one('product.subfamilia', 'Subfamily')


class ProductAtributos(models.Model):
    _name = 'product.atributos'
    _description = 'Atributos Nutrition Facts'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Attributes', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)
    # product_ids = fields.Many2many('product.template', 'product_atributos_rel', 'atributos_id', 'prod_id', string='Producto')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A tag with that name already exists!"),
    ]
