# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except
# -

from datetime import datetime
import logging
from odoo import models, fields, _
from odoo.exceptions import MissingError
from odoo import http
from odoo.addons.web.controllers.main import serialize_exception,content_disposition 

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


class SaleOrderType(models.Model):
    """Sale order type: Presential, App Mobile, Metaverse Etc."""

    _name = 'sale.order.type'
    _description = 'Sale order type'

    name = fields.Char('Name')
    code = fields.Char('Code', size=4)
    description = fields.Char('Description')


class SaleOrder(models.Model):
    """Sale order model by Api Mobile."""

    _inherit = 'sale.order'


    sale_order_type = fields.Many2one('sale.order.type',
            string='Presential purchase in a physical store')

    def _get_sale_order_from_controller(self, login):
        """Get sale order from controller."""

        domain = [('login', '=', login)] if type(login) == str else [('id', '=', login)]
        user_id = self.env['res.users'].search(domain)
        if not user_id:
            return {"status": "400",
                    "message": "Usuario {} no existe".format(login)}

        order = self._search_sale_order_by_partner(user_id.partner_id.id)
        if not order:
            return {"status": "400",
                    "message": "Usuario {} no posee ninguna orden de venta.".\
                            format(login)}

        list_sale = self._list_sale_order_cart(order)
        return list_sale

    def _add_products_from_controller(self, userid, barcode, quantity, sensor,
                                      action=None):
        """Add prodcuts from controllers."""

        domain = [('login', '=', userid)] if type(userid) == str else [('id', '=', userid)]
        user_id = self.env['res.users'].search(domain)
        order = self._search_sale_order_by_partner(user_id.partner_id.id)
        _logger.info('EL usuario:{}, tiene la orden:{}'.format(order,
            user_id.partner_id))

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

    def is_pending_order_to_pay(self):
        """Validate if user has be opending order to pay."""
        if not self:
            return False

        try:
            self.ensure_one()
            return bool(self.amount_total)
        except Exception as error:
            _logger.error(error)
        return True

    def is_payment_approved(self):
        """Validate is payment_prisma_status is approved."""

        self.ensure_one()
        status_paid = self.payment_prisma_status_ids.status
        if status_paid == 'approved':
            return True
        return False

    def cancel_sale_order(self):
        """Cancel sale order."""

        self.ensure_one()
        try:
            self.action_cancel()
        except Exception as Error:
            _logger.info(Error)
            return False

        return True

    def confirm_sale_order(self):
        """Confirm sale order."""

        self.ensure_one()
        try:
            self.action_confirm()
        except Exception as Error:
            _logger.info(Error)
            return False

        return True

    def create_sale_order(self, partner_id, store_id):
        """Create sale order."""

        # Si ya existe una orden Abierta para este usuario con estado draft
        # no no crear la Orden de venta para que se use esta
        if self._search_sale_order_by_partner(partner_id):
            return True

        user_id = self.env['res.users'].search([('login', '=', 'admin')],
                                               limit=1)

        order_vals = {'partner_id': partner_id,
                      'validity_date': datetime.utcnow().strftime(
                          '%Y-%m-%d %H:%M:%S'),
                      'warehouse_id': int(store_id),
                      'user_id': user_id.id,
                      'order_line': [],
                      }
        _logger.info(order_vals)

        new_order = self.create(order_vals)
        new_order._cr.commit()
        return True

    def get_sale_order_list(self, login, page=1, order_for_page=6):
        """Get sale order list by res.partner whith status sale."""

        ORDER_FOR_PAGE = order_for_page
        user_id = self.env['res.users'].search([('login', '=', login)])
        orders = self._search_sale_order_by_partner(user_id.partner_id.id,
                                                    'sale')
        _logger.info('Ordenes: {}'.format(orders))

        filters = orders.search([('id', 'in', orders.ids)],
                                offset=(page - 1) * ORDER_FOR_PAGE,
                                limit=ORDER_FOR_PAGE)
        _logger.info('Filters: {}'.format(filters))

        order_list = []

        for order in filters:
            data = {}
            _logger.info('order: {}'.format(order.name))
            payments = [(t.bin, t.card_type, t.card_brand, t.status)
                        for t in order.payment_prisma_attempt_ids]

            data = {"order": order.name,
                    "create_date": order.create_date.strftime(
                        "%Y-%m-%d, %H:%M:%S"),
                    "store": order.user_id.name,
                    "amount_total": order.amount_total,
                    "download_invoice": self._link_download_invoice(order),
                    "payments": payments
                    }
            order_list.append(data)

        return order_list

    def create_pdf(self, order):
        """Method for create pdf invoice."""

        for invoice in order.invoice_ids:
            pdf, _ = self.env['ir.actions.report']._get_report_from_name(
                'account.report_invoice').sudo()._render_qweb_pdf(
                            [int(invoice.id)])
            pdf_http_headers = [('Content-Type', 'application/pdf'),
                                ('Content-Length', len(pdf)),
                                ('Content-Disposition', 'mifactura')]
            response = http.request.make_response(pdf, headers=pdf_http_headers)

    def _link_download_invoice(self, order):
        """prepare download link invoice from sale order passed."""

        links = []
        server = self.env['ir.config_parameter'].search([
            ('key', '=', 'web.base.url')]
        )
        if not server.value:
            return ''

        # self.create_pdf(order)

        try:
            for invoice in order.invoice_ids:

                link = ''
                new = invoice.get_portal_url()
                access_url = invoice.access_url
                access_token = invoice.access_token
                command = '&report_type=pdf'
                # command = '&report_type=pdf&download=true'
                link = f"{server.value}{new}{command}"
                # link = f"{server.value}{access_url}?access_token={access_token}{command}"
                # link = f"{server.value}{access_url}?{command}"
                _logger.info(link)
                links.append(link)
        except Exception as error:
            print(error)
            _logger.info(error)
            links = error

        return links

    def _search_sale_order_by_partner(self, partner_id=None, state='draft'):
        """Search sale order by partner id."""

        order_sale = self.search([
            ('partner_id', '=', partner_id),
            ('state', '=', state)], 
            order="datetime desc", limit=1)
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
        sensor_dom = [('name', '=', sensor)] if type(sensor) == str else [('id', '=', sensor)]
        sensor_id = self.env['store.sensor'].search(sensor_dom).id
        product_store = self.env['product.store'].search(
            [('product_id', '=', product.id),
             ('shelf_id', '=', sensor_id),
             ('store_id', '=', store.id)
             ]
        )
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
        product_store = self.env['product.store'].search(
            [('product_id', '=', product.id),
             ('shelf_id.name', '=', sensor),
             ('store_id', '=', store.id)]
        )

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
        """Add products to cart."""

        _logger.info('Orden:{} - Producto:{}'.format(order_instance,
            product_instance))

        quantity = quantity
        product = self._product_in_sale_order(order_instance, product_instance)
        if product:
            quantity += product.product_uom_qty
            product.write({'product_uom_qty': quantity})
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
            _logger.error(error)

        return False

    def _remove_product_cart(self, order_instance, product_instance, quantity):
        """remove products from cart."""

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
        """Get list products, amount total, payment method from
           sale order pased."""

        payments = [(t.bin, t.card_type, t.card_brand, t.status)
                    for t in order_instance.payment_prisma_attempt_ids]

        result = []
        domain = [('id', '=', order_instance.id)]
        header = order_instance.search_read(domain, [
            'name', 'amount_total', 'cart_quantity', 'amount_undiscounted',
            'amount_untaxed', 'state']
            )

        header[0]["create_date"] = order_instance.create_date.strftime("%Y-%m-%d, %H:%M:%S")
        header[0]["payments"] = payments
        header[0]["address"] = order_instance.warehouse_id.direccion_local
        header[0]["store"] = order_instance.warehouse_id.name

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
            product_image = None if not line.product_id.image_128 else \
                    line.product_id.image_128.decode('ascii')
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
