# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
    peso_estante = fields.Integer('Peso total del estante (g)', compute='_get_peso_estante')
    aptitud = fields.Integer('Porcentaje de aptitud de vida útil', required=True, default=70)
    desc_tag = fields.Char('Descripción corta del TAG', required=True)

    @api.depends('peso_bruto', 'cant_frente', 'cant_fondo', 'cant_altura')
    def _get_peso_estante(self):
        self.peso_estante = self.peso_bruto * self.cant_frente * self.cant_fondo * self.cant_altura


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


