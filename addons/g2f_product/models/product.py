# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sector = fields.Many2one('product.sector', 'Sector', required=True)
    familia = fields.Many2one('product.familia', 'Familia', required=True)
    subfamilia = fields.Many2one('product.subfamilia', 'Subfamilia', required=True)
    categoria = fields.Many2one('product.categoria', 'Categoría', required=True)
    alto = fields.Integer('Alto (mm)', required=True)
    ancho = fields.Integer('Ancho (mm)', required=True)
    profundidad = fields.Integer('Profundidad (mm)', required=True)
    peso_bruto = fields.Integer('Peso bruto (g)', required=True)
    layout = fields.Selection(selection=[('S', 'Seco'), ('F', 'Frio'), ('C', 'Congelado')], required=True)
    cant_frente = fields.Integer('Cantidad de unidades por frente', required=True)
    cant_fondo = fields.Integer('Cantidad de unidades por fondo', required=True)
    cant_altura = fields.Integer('Cantidad de unidades por altura', required=True)
    gondola = fields.Char('Posición en góndola', required=True, size=14)
    peso_estante = fields.Integer('Peso total del estante', compute='_get_peso_estante')
    aptitud = fields.Integer('Porcentaje de aptitud de vida útil', required=True, default=70)
    desc_tag = fields.Char('Descripción corta del TAG', required=True)
    atributos_ids = fields.Many2many('product.atributos', 'product_atributos_rel', 'prod_id', 'atributos_id', string='Atributos')

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
            raise UserError(_('El campo (Posición en góndola: %s) debe contener 14 caracteres', vals['gondola']))
        if 'cant_frente' in vals and int(vals['cant_frente']) == 0:
            raise UserError(_('El campo (Cantidad de unidades por frente: %s) debe ser mayor a cero',
                              vals['cant_frente']))
        if 'cant_fondo' in vals and int(vals['cant_fondo']) == 0:
            raise UserError(_('El campo (Cantidad de unidades por fondo: %s) debe ser mayor a cero',
                              vals['cant_fondo']))
        if 'cant_altura' in vals and int(vals['cant_altura']) == 0:
            raise UserError(_('El campo (Cantidad de unidades por altura: %s) debe ser mayor a cero',
                              vals['cant_altura']))
        return super(ProductTemplate, self).write(vals)


class ProductSector(models.Model):
    _name = 'product.sector'
    _description = 'Sector'

    nro = fields.Integer('Nro. Sector')
    name = fields.Char('Sector')


class ProductFamilia(models.Model):
    _name = 'product.familia'
    _description = 'Familia'

    nro = fields.Integer('Nro. Familia')
    name = fields.Char('Familia')
    sector = fields.Many2one('product.sector', 'Sector')


class ProductSubfamilia(models.Model):
    _name = 'product.subfamilia'
    _description = 'Subfamilia'

    nro = fields.Integer('Nro. Subfamilia')
    name = fields.Char('Subfamilia')
    familia = fields.Many2one('product.familia', 'Familia')


class ProductCategoria(models.Model):
    _name = 'product.categoria'
    _description = 'Categoria'

    nro = fields.Integer('Nro. Categoría')
    name = fields.Char('Categoría')
    subfamilia = fields.Many2one('product.subfamilia', 'Subfamilia')


class ProductAtributos(models.Model):
    _name = 'product.atributos'
    _description = 'Atributos Nutrition Facts'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Atributos', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)
    # product_ids = fields.Many2many('product.template', 'product_atributos_rel', 'atributos_id', 'prod_id', string='Producto')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Ya existe una etiqueta con ese nombre !"),
    ]
