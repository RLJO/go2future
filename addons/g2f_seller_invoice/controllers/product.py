# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from json import dumps
import requests
from odoo import http, _
import json
import logging
_logger = logging.getLogger(__name__)


class Product(http.Controller):
    @http.route('/product/widget/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_product_widget(self, **kw):
        code = kw.get('code')
        product_tmpl = http.request.env['product.template']
        response = product_tmpl.sudo()._get_product_widget(code)
        print(http.request.params)
        print(response)
        # return json.dumps({"result": "Success"})
        return response

    @http.route('/product/planos/', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_product_planos(self, **kw):
        code = kw.get('code')
        product_tmpl = http.request.env['product.template']
        response = product_tmpl.sudo()._get_product_planos(code)
        print(http.request.params)
        print(response)
        return response

    # Nombre del endpoint:
    #
    # /product/planos/
    #
    # Consulta de plano:
    #
    # {
    # "params": {
    # "code": "0001"
    # }
    # }
    #
    # Respuesta de Odoo
    #
    # {
    # "jsonrpc": "2.0",
    # "id": null,
    # "result": {
    # "data": [
    # {
    # "ARTICLE_ID": "7790070621115", //Código EAN
    # "ITEM_NOMBRE": "ACONDICIONADOR OLEO NUTRICION", //Nombre del producto
    # "ITEM_STOCK": 50.0, // Stock del producto en el local
    # "ITEM_FIRST_LINE": "ACONDICIONADOR", //Descripción corta del TAG
    # "ITEM_SECOND_LINE": OLEO NUTRICION, //Descripción 2 corta del TAG
    # "ITEM_BRAND": "DOVE", //Marca
    # "ITEM_VOLUME": 400, //Volumen
    # "ITEM_VOLUME_MEASUREMENT": "ml", //Unidad de medida de venta
    # "ITEM_SECTOR": "PERFUMERIA", //Sector de la estructura mercadológica
    # "ITEM_FAMILIA": "CUIDADO Y BELLEZA DEL CABELLO", //Familia de la estructura mercadológica
    # "ITEM_SUBFAMILIA": "ACONDICIONADORES", //Subfamilia de la estructura mercadológica
    # "ITEM_CATEGORIA": "GENERICO", //Categoría de la estructura mercadológica
    # "ITEM_VENDEDOR": "UNILEVER DE ARGENTINA S.A.", //Vendedor
    # "ITEM_CANT_VENDIDA": "150", // Cantidad vendida los últimos 30 días
    # }
    # ]
    # }
    # }

# curl -i -X POST -H "Content-Type: application/json" -d '{"params": {"code":"GO1"}}' 'https://g2f-api-rest.odoo.com/product/widget/'