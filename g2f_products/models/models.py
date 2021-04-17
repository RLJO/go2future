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

    precio_por_kg = fields.Float(string='Precio por Kg')
    precio_por_l = fields.Float(string='Precio por l')

    descripcion_audible = fields.Char(string='Descripción audible del producto')

    contenido_azucar = fields.Float(string='Contenido de azúcar')

    #type -> Campo selección debe ser por defecto Almacenable

    type = fields.Selection(default='product')
    
    #company_id -> Por defecto debe ser la compañía del vendedor logueado


