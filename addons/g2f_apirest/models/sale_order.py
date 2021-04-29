# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except
# -

from datetime import datetime
from json import dumps
import logging
from odoo import models, fields, api, _

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    '''Sale order model by Api Mobile.'''

    _inherit = 'sale.order'

    def _get_sale_order_from_controller(self, login):
        user_id = self.env['res.users'].search([('login', '=', login)])
        order = self._search_sale_order_by_partner(user_id.partner_id.id)
        list_sale = self._list_sale_order_cart(order)
        return list_sale

    def _add_products_from_controller(self, user_id, product_id, quantity,
                                      action=None):
        order = self._search_sale_order_by_partner(user_id)
        product = self._search_product_by_id(product_id)
        if action == 'picked':
            self._add_product_cart(order, product, quantity)
            return True
        elif action == 'returned':
            self._remove_product_cart(order, product, quantity)
            return True

        return False

    def create_sale_order(self, partner_id):
        '''Create sale order.'''

        # Si ya existe una orden Abierta para este usuario con estado draft
        # no no crear la Orden de venta para que se use esta
        if self._search_sale_order_by_partner(partner_id):
            return True

        order_vals = {'partner_id': partner_id,
                'validity_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': []}

        new_order = self.create(order_vals)
        new_order._cr.commit()
        return True

    def _search_sale_order_by_partner(self, partner_id=None, state='draft'):
        '''Search sale order by partner id.'''

        order_sale = self.search([
            ('partner_id', '=', partner_id),
            ('state', '=', state)])
        return order_sale

    def _search_product_by_id(self, product_id=None):
        return self.env['product.product'].search([('id', '=', product_id)])

    def _product_in_sale_order(self, order_instance, product_instance):
        return order_instance.order_line.search([
            ('order_id', '=', order_instance.id),
            ('product_id', '=', product_instance.id)
            ])

    def _add_product_cart(self, order_instance, product_instance, quantity):
        '''Add products to cart.'''

        quantity = quantity
        product = self._product_in_sale_order(order_instance, product_instance)
        if product:
            quantity += product.product_uom_qty
            product.write({'product_uom_qty': quantity})
            product._cr.commit()
            return True

        line_vals = {
                'order_id': order_instance.id,
                'product_id': product_instance.id,
                'name': product_instance.name,
                'product_uom_qty': quantity,
                'price_unit': product_instance.list_price
                }

        try:
            order_instance.order_line.create(line_vals)
            return True
        except Exception as error:
            print(error)
        return False

    def _remove_product_cart(self, order_instance, product_instance, quantity):
        '''remove products from cart.'''

        quantity = quantity
        product = self._product_in_sale_order(order_instance, product_instance)
        if product:
            quantity = product.product_uom_qty - quantity
            product.write({'product_uom_qty': quantity})
            product._cr.commit()
            return True
        return False

    def _list_sale_order_cart(self, order_instance):
        result = []
        domain = [('id', '=', order_instance.id)]
        header = order_instance.search_read(domain, [
            'name', 'amount_total', 'cart_quantity',
            'state']
            )

        result.append(header)
        lines = order_instance.search(domain).order_line
        title = ['product_name', 'product_sku', 'product_image',
                'price_unit', 'product_uom_qty', 'price_subtotal',
                'price_tax', 'price_total', 'product_uom',
                'product_type']

        for line in lines:
            product_name = line.product_id.name
            product_sku = line.product_id.default_code
            product_image = line.product_id.image_128.decode('ascii')
            price_unit = line.price_unit
            product_uom_qty = line.product_uom_qty
            price_subtotal = line.price_subtotal
            price_tax = line.price_tax
            price_total = line.price_total
            product_uom = line.product_uom.name
            product_type = line.product_type
            result.append(dict(zip(title, [
                product_name, product_sku, product_image, price_unit,
                product_uom_qty, price_subtotal, price_tax, price_total,
                product_uom, product_type])))
        print(result)
        return result
