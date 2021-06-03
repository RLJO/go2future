#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class website_voucher(WebsiteSale):

	@http.route()
	def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
		response = super(website_voucher, self).payment_validate(transaction_id=transaction_id, sale_order_id=sale_order_id, **post)
		if sale_order_id is None:
			sale_order_id = request.session.get('sale_last_order_id')
		order = request.env['sale.order'].sudo().browse(sale_order_id)
		product_id = request.env['ir.default'].sudo().get('res.config.settings', 'wk_coupon_product_id')
		is_voucher_line = order.order_line.filtered(lambda x: x.wk_voucher_id and x.product_id.id == product_id)
		if is_voucher_line:
			# self.env['voucher.voucher'].sudo().return_voucher(line.wk_voucher_id.id, line.id)
			history_obj = request.env['voucher.history'].sudo().search([('sale_order_line_id','=',is_voucher_line.id)])
			if history_obj:
				history_obj.state = 'done'
		if order and not order.amount_total:
			return request.redirect('/shop/confirmation')
		return response

	@http.route('/website/voucher/', type='json',  auth="public", methods=['POST'], website=True)
	def voucher_call(self, secret_code=False, **post):
		try:
			result = {}
			voucher_obj = request.env['voucher.voucher']
			order= request.website.sale_get_order()
			wk_order_total = order.amount_total
			partner_id = request.env['res.users'].browse(request.uid).partner_id.id
			products =  []
			for line in order.order_line:
				products.append(line.product_id.id)
			result = voucher_obj.sudo().validate_voucher(secret_code, wk_order_total, products, refrence="ecommerce", partner_id=partner_id)
			if result['status']:
				final_result = request.website.sale_get_order(force_create=1)._add_voucher(wk_order_total, result)
				if not final_result['status']:
					result.update(final_result)
				request.session['secret_key_data'] = {'coupon_id':result['coupon_id'],'total_available':result['total_available'],'wk_voucher_value':result['value'],'voucher_val_type':result['voucher_val_type'],'customer_type':result['customer_type']}
			return result
		except Exception as e:
			_logger.info('-------------Exception-----%r',e)

	@http.route(['/shop/cart/voucher_remove/<int:line_id>'], type='http', auth="public",  website=True)
	def remove_voucher(self, line_id, **post):
		try:
			line_obj = request.env["sale.order.line"].sudo().browse(int(line_id))
			if line_obj.exists():
				line_obj.sudo().unlink()
				request.session['secret_key_data'] = {}
		except Exception as e:
			_logger.info('-------------Exception-----%r',e)
		return request.redirect("/shop/cart/")
