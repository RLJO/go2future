#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class WebsiteStock(http.Controller):

	@http.route('/add/bundle/variants', type='json', auth='public', website=True)
	def add_bundle_variants(self, jsonList=False, pack_id=False):
		order = request.website.sale_get_order(force_create=1)
		order_line_selected_varinats = []
		pack_description = ''
		final_description = ''
		if order:
			if jsonList:
				for line in jsonList:
					order_line_variant_data = {}
					order_line_variant_data['variant_id'] = int(line['variant_id'])
					order_line_variant_data['quantity_in_pack'] = int(line['quantity'])
					order_line_selected_varinats.append((0,0,order_line_variant_data))
					prod_obj = request.env['product.product'].sudo().browse(int(line['variant_id']))
					pack_description += '%s::Qty=%s,\n'%(prod_obj.display_name, line['quantity'])
				if pack_id:
					pack_obj = request.env['product.template'].sudo().browse(int(pack_id))
					for pack_varinat in pack_obj.product_variant_ids:
						final_description += '%s\n%s'%(pack_varinat.name,pack_description)
						request.env['sale.order.line'].sudo().create({'order_id':order.id,'product_id':pack_varinat.id,'price_unit':pack_varinat.list_price,'product_uom':1,'product_uom_qty':1, 'wk_product_variants':order_line_selected_varinats,'name':final_description})
					return '/shop/cart'
			else:
				return False
