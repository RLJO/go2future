# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class Product(models.Model):

    _inherit = 'product.template'

    vegano = fields.Boolean(string = 'Apto veganos')
    contiene_tacc = fields.Boolean(string = 'Contiene TACC')
    organico = fields.Boolean(string = 'Orgánico')
    
    nombre_producto_linea_1 = fields.Char(string = 'Linea 1 para Display', size=16)
    nombre_producto_linea_2 = fields.Char(string = 'Línea 2 para Display', size=16)

    url_link_video_entrenamiento = fields.Char(string = 'URL al video de entrenamiento')

    precio_por_kg = fields.Float(compute='_precio_por_kg', store=True, string='Precio por Kg')
    precio_por_l = fields.Float(compute='_precio_por_l', store=True, string='Precio por l')

    descripcion_audible = fields.Char(string='Descripción audible del producto')

    contenido_azucar = fields.Float(string='Contenido de azúcar')

    #type -> Campo selección debe ser por defecto Almacenable

    type = fields.Selection(default='product')
    
    #company_id -> Por defecto debe ser la compañía del vendedor logueado

    @api.depends('weight')
    def _precio_por_kg(self):

        for record in self:

            if record.weight != 0:

                record.precio_por_kg = record.list_price / record.weight

    @api.depends('volume')
    def _precio_por_l(self):

        for record in self:

            if record.volume != 0:

                record.precio_por_l = record.list_price / record.volume


    

    


