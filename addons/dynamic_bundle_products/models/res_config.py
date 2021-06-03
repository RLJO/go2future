#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _

class DynamicBundleProductConfig(models.Model):
	_name = 'dynamic.bundle.products.config'
	_inherit = 'webkul.website.addons'

	amount_saved_in_product_page = fields.Boolean('Show amount saved ribbon in Product Details Page')

	

	def set_values(self):
		super(DynamicBundleProductConfig, self).set_values()
		IrDefault = self.env['ir.default'].sudo()
		IrDefault.set('dynamic.bundle.products.config', 'amount_saved_in_product_page',self.amount_saved_in_product_page)
		return True


	def get_values(self):
		res = super(DynamicBundleProductConfig, self).get_values()
		IrDefault = self.env['ir.default'].sudo()
		res.update(
			{
			'amount_saved_in_product_page':IrDefault.get('dynamic.bundle.products.config', 'amount_saved_in_product_page'),
			}
		)
		return res