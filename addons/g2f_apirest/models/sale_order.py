# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except
# -

from datetime import datetime
from json import dumps
import logging
from odoo import models, fields, api, _
from odoo.exceptions import MissingError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


def validate_product_exist(search_product_method):
    """Decorator validate prodcut exist."""
    def exceptions(*args, **kwargs):
        """Search products."""
        product = search_product_method(*args, **kwargs)
        if not product:
            raise MissingError(_("Product does not exist in Store."))
        return product
    return exceptions


class SaleOrder(models.Model):
    '''Sale order model by Api Mobile.'''

    _inherit = 'sale.order'

    def _get_sale_order_from_controller(self, login):
        """Get sale order from controller."""

        user_id = self.env['res.users'].search([('login', '=', login)])
        order = self._search_sale_order_by_partner(user_id.partner_id.id)
        list_sale = self._list_sale_order_cart(order)
        return list_sale

    def _add_products_from_controller(self, userid, barcode, quantity, sensor,
                                      action=None):
        """Add prodcuts from controllers."""

        user_id = self.env['res.users'].search([('id', '=', userid)])
        order = self._search_sale_order_by_partner(user_id.partner_id.id)
        product = self._search_product_by_id(barcode)
        if action == 'picked':
            self._add_product_cart(order, product, quantity)
            self._remove_product_shelf(order, product, quantity, sensor)
            return True
        elif action == 'placed':
            self._remove_product_cart(order, product, quantity)
            self._add_product_shelf(order, product, quantity, sensor)
            return True

        return False

    def is_paid(self):
        """Validate is payment_prisma_status is approved."""

        self.ensure_one()
        status_paid = self.payment_prisma_status_ids.status
        if status_paid == 'approved':
            return True
        return False

    def confirm_sale_order(self):
        """Confirm sale order."""

        self.ensure_one()
        try:
            self.action_confirm()
        except Exception as Error:
            _logger.info(Error)
            return False

        return True

    def create_sale_order(self, partner_id):
        '''Create sale order.'''

        # Si ya existe una orden Abierta para este usuario con estado draft
        # no no crear la Orden de venta para que se use esta
        if self._search_sale_order_by_partner(partner_id):
            return True

        order_vals = {'partner_id': partner_id,
                'validity_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': [],
                }

        new_order = self.create(order_vals)
        new_order._cr.commit()
        return True

    def get_sale_order_list(self, login, page=1):
        """Get sale order list by res.partner whith status sale."""

        ORDER_FOR_PAGE = 2
        user_id = self.env['res.users'].search([('login', '=', login)])
        orders = self._search_sale_order_by_partner(user_id.partner_id.id,
                                                    'sale')
        filters = orders.search([('id', 'in', orders.ids)],
                                offset=(page - 1) * ORDER_FOR_PAGE,
                                limit=ORDER_FOR_PAGE)
        order_list = []

        for order in filters:
            data = {}
            # Por ahora se saca el stado paid porque la factura aparece como
            # que no se pago
            # if order.invoice_ids and order.invoice_ids.payment_state.lower() == 'paid':
            if order.invoice_ids:
                data = {"order": order.name,
                        "create_date": order.create_date.strftime("%Y-%m-%d"),
                        "store": order.user_id.name,
                        "amount_total": order.amount_total,
                        "download_invoice": self._link_download_invoice(order)
                        }
                order_list.append(data)

        return order_list

    def _link_download_invoice(self, order):
        """prepare download link invoice from sale order passed."""

        links = []
        server = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])
        if not server.value:
            return ''

        try:
            for invoice in order.invoice_ids:
                link = ''
                access_url = invoice.access_url
                access_token = invoice.access_token
                command = '&report_type=pdf&download=true'
                # link = f"{server.value}{access_url}?access_token={access_token}{command}"
                link = f"{server.value}{access_url}?{command}"
                _logger.info(link)
                links.append(link)
        except Exception as error:
            print(error)
            _logger.info(error)
            links = error

        return links

    def _search_sale_order_by_partner(self, partner_id=None, state='draft'):
        '''Search sale order by partner id.'''

        order_sale = self.search([
            ('partner_id', '=', partner_id),
            ('state', '=', state)])
        return order_sale

    @validate_product_exist
    def _search_product_by_id(self, barcode=None):
        return self.env['product.product'].search([('barcode', '=', barcode)])

    def _product_in_sale_order(self, order_instance, product_instance):
        return order_instance.order_line.search([
            ('order_id', '=', order_instance.id),
            ('product_id', '=', product_instance.id)
            ])

    def _add_product_shelf(self, order, product, quantity, sensor):
        quantity = quantity
        store = order.warehouse_id
        product_store = self.env['product.store'].search([('product_id', '=', product.id),
                                                          ('shelf_id', '=', sensor),
                                                          ('store_id', '=', store.id)])
        try:
            if product_store:
                quantity += product_store.qty_available_prod
                product_store.write({'qty_available_prod': quantity})
                product_store._cr.commit()
            return True
        except Exception as error:
            print(error)
            _logger.info(error)

    def _remove_product_shelf(self, order, product, quantity, sensor):
        quantity = quantity
        store = order.warehouse_id
        product_store = self.env['product.store'].search([('product_id', '=', product.id),
                                                          ('shelf_id.name', '=', sensor),
                                                          ('store_id', '=', store.id)])
        # _product_in_sale_order(order_instance, product_instance)
        try:
            if product_store:
                quantity = product_store.qty_available_prod - quantity
                product_store.write({'qty_available_prod': quantity})
                product_store._cr.commit()
            return True
        except Exception as error:
            print(error)
            _logger.info(error)

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
                'seller': product_instance.seller_ids.name.id,
                'name': product_instance.name,
                'product_uom_qty': quantity,
                'price_unit': product_instance.list_price
                }

        try:
            order_instance.order_line.create(line_vals)
            return True
        except Exception as error:
            print(error)
            _logger.info(error)

        return False

    def _remove_product_cart(self, order_instance, product_instance, quantity):
        '''remove products from cart.'''

        quantity = quantity
        product = self._product_in_sale_order(order_instance, product_instance)
        if product.product_uom_qty > 1:
            quantity = product.product_uom_qty - quantity
            product.write({'product_uom_qty': quantity})
            product._cr.commit()
            return True
        elif product.product_uom_qty == 1:
            product.unlink()
            product._cr.commit()
            return True
        return False

    def _list_sale_order_cart(self, order_instance):
        result = []
        domain = [('id', '=', order_instance.id)]
        header = order_instance.search_read(domain, [
            'name', 'amount_total', 'cart_quantity', 'amount_undiscounted',
            'amount_untaxed', 'state']
            )

        result.append(header)
        lines = order_instance.search(domain).order_line
        title = ['product_name', 'product_sku', 'product_image',
                 'price_unit', 'product_uom_qty', 'discount',
                 'discount_amount', 'price_subtotal',
                 'price_tax', 'price_total', 'product_uom',
                 'product_type', 'barcode']

        for line in lines:
            product_barcode = line.product_id.barcode
            product_name = line.product_id.name
            product_sku = line.product_id.default_code
            product_image = None if not line.product_id.image_128 else line.product_id.image_128.decode('ascii')
            price_unit = line.price_unit
            product_uom_qty = line.product_uom_qty
            product_discount = line.discount
            product_discount_amount = line.price_unit * (line.discount / 100)
            price_subtotal = line.price_subtotal
            price_tax = line.price_tax
            price_total = line.price_total
            product_uom = line.product_uom.name
            product_type = line.product_type
            result.append(dict(zip(title, [
                product_name, product_sku, product_image, price_unit,
                product_uom_qty, product_discount, product_discount_amount,
                price_subtotal, price_tax, price_total, product_uom,
                product_type, product_barcode])))
        print(result)
        return result
