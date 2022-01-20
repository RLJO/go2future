# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import timedelta, time
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_product_widget(self, code):
        data = {"data": []}
        pricelist = self.env['product.pricelist.item']
        location_ids = self.env['stock.location'].search([('location_id.name', '=', code)])
        quant = self.env['stock.quant']
        quant_ids = quant.search([('location_id', 'in', location_ids.ids)], order='location_id')
        for line in quant_ids:
            second_line = line.product_id.brand + ' ' if line.product_id.brand else ''
            second_line += str(line.product_id.contents) + ' ' if line.product_id.contents else ''
            second_line += line.product_id.uom_id.name
            deals = pricelist.search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('website_deals_m2o.state', '=', 'validated')
            ])
            # discounted_price, percent_price = self.get_deals(line)
            if deals:
                discounted_price = deals.discounted_price
                percent_price = deals.percent_price
            else:
                discounted_price = 0.0
                percent_price = 0.0
            head = {
                "ARTICLE_ID": line.product_id.barcode,
                "ITEM_STOCK": line.quantity,
                "ITEM_FIRST_LINE": line.product_id.desc_tag,
                "ITEM_SECOND_LINE": line.product_id.desc_tag_2,
                "ITEM_BRAND": line.product_id.brand,
                "ITEM_VOLUME": line.product_id.contents,
                "ITEM_VOLUME_MEASUREMENT": line.product_id.uom_id.name,
                "ITEM_PRICE": str(line.product_id.list_price),
                "ITEM_REFERENCE_PRICE": line.product_id.uom_price.split()[1],
                "ITEM_REFERENCE_PRICE_MEASUREMENT": line.product_id.uom_price.split()[0],
                "ITEM_LOCATION": code + '/' + line.location_id.name,

                "OFFER": {
                    "SALE_PRICE": discounted_price,
                    "SALE_PERCENT": percent_price
                }
            }
            data["data"].append(head)
        if not quant_ids:
            data = 'No se encontró Minigo registrado con el id: %s' % code
        return data

    @api.model
    def _get_product_planos(self, code):
        data = {"data": []}
        location_ids = self.env['stock.location'].search([('location_id.name', '=', code)])
        quant = self.env['stock.quant']
        quant_ids = quant.search([('location_id', 'in', location_ids.ids)], order='location_id')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in quant_ids:
            second_line = line.product_id.brand + ' ' if line.product_id.brand else ''
            second_line += str(line.product_id.contents) + ' ' if line.product_id.contents else ''
            second_line += line.product_id.uom_id.name or ''
            qty_sold = line.product_id._compute_sales_count_wo_group()
            head = {
                "ARTICLE_ID": line.product_id.barcode,
                "ITEM_NAME": line.product_id.name,
                "ITEM_STOCK": line.quantity,
                "ITEM_FIRST_LINE": line.product_id.desc_tag,
                "ITEM_SECOND_LINE": line.product_id.desc_tag_2,
                "ITEM_BRAND": line.product_id.brand,
                "ITEM_VOLUME": line.product_id.contents,
                "ITEM_VOLUME_MEASUREMENT": line.product_id.uom_id.name,
                "ITEM_SECTOR": line.product_id.sector.name,
                "ITEM_FAMILY": line.product_id.familia.name,
                "ITEM_SUBFAMILY": line.product_id.subfamilia.name,
                "ITEM_CATEGORY": line.product_id.categoria.name,
                "ITEM_SELLER": line.product_id.marketplace_seller_id.name,
                "ITEM_QTY_SOLD": line.product_id.sales_count,
                "ITEM_WIDTH": line.product_id.alto,
                "ITEM_HEIGHT": line.product_id.ancho,
                "ITEM_DEPTH": line.product_id.profundidad,
                "ITEM_WEIGHT": line.product_id.peso_bruto,
                "ITEM_LAYOUT": line.product_id.layout,
                "ITEM_URL_3D_FILE": line.product_id.product_url,
                "UNIT_PRICE": line.product_id.product_tmpl_id.list_price,
                "PRODUCT_DESCRIPTION": line.product_id.product_tmpl_id.product_description,
                "PRODUCT_URL": base_url + '/web/image?' + 'model=product.template&id=' + str(line.product_id.product_tmpl_id.id) + '&field=image_128',
                # "PRODUCT_IMAGE": line.product_id.product_tmpl_id.image_128.decode("utf-8") if line.product_id.product_tmpl_id.image_128 else False
                }
            data["data"].append(head)
        if not quant_ids:
            data = 'No se encontró Minigo registrado con el id: %s' % code
        return data

    @api.model
    def get_product_data(self, vals):
        domain = [('type', '=', 'product')]
        data = {"dataList": []}
        if vals:
            domain = [
                ('default_code', '=', vals['sku']),
                ('type', '=', 'product')
            ]
        product_ids = self.search(domain)
        for product in product_ids:
            second_line = product.brand + ' ' if product.brand else ''
            second_line += str(product.contents) + ' ' if product.contents else ''
            second_line += product.uom_id.name
            head = {
                "stationCode": "G2F",
                "id": product.default_code,
                "name": product.name,
                "nfc": "https://minigo-visual-impairment.s3-sa-east-1.amazonaws.com/iTANKRDes.mp3",
                "originPrice": False,
                "salePrice": False,
                "discountPercent": False,
                "data": {
                    "ARTICLE_ID": product.default_code,
                    "ITEM_FIRST_LINE": product.desc_tag,
                    "ITEM_SECOND_LINE": second_line,
                    "SALE_PRICE": str(product.list_price),
                    "LITER_PRICE": "0",
                    "WEIGHT_UNIT": "0"
                }
            }
            data["dataList"].append(head)
        if not product_ids:
            data = 'No se encontró producto registrado con el SKU: %s' % vals['sku']
        return data


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_sales_count_wo_group(self):
        r = {}
        self.sales_count = 0
        # if not self.user_has_groups('sales_team.group_sale_salesman'):
        #     return r
        date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                      time.min))

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            product.sales_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r

# class ProductTemplate(http.Controller):
#     @http.route(['/product/list'], type='http', auth='public',
#                 methods=['POST'], website=True, csrf=False)
#     def get_product_data_list(self):
#         return 'Ejecutar aqui un post a la API de los indios'

    #curl --location --request GET 'http://127.0.0.1:8075/camera_ports/?ai_unit=1' --header 'Content-Type: application/json' --data-raw