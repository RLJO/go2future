#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from openerp.tools.translate import _
from odoo.exceptions import UserError , ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductBundleWizard(models.TransientModel):
	_name = 'product.bundle.wizard' 	
	_description = "Bundle Product Wizard"

	pack_id = fields.Many2one('product.template',string='Bundle Product')
	product_id = fields.Many2one('product.product',string='Add An Item')
	template_lines = fields.One2many(comodel_name = 'pack.template.lines', inverse_name = 'bundle_product_wizard_id',string = 'Product pack')
	product_lines = fields.One2many(comodel_name = 'pack.product.lines', inverse_name = 'bundle_product_wizard_id',string = 'Product Pack Lines')
	pack_quantity = fields.Integer('Pack Quantity' ,required=True, default="1")
	description = fields.Html(compute='get_description_table', string="Description_one")

	@api.depends('pack_id')
	def get_description_table(self):
		message = ''
		if self.pack_id:
			if self.pack_id.wk_bundle_products:
				if self.pack_id.bundle_type == 'fixed_quantity':
					message += '<center><table border=1 class="col-md-12" style="margin-left:250px"><tr class="alert-info" ><th>Product<th><th>Quantity<th></tr>'
				if self.pack_id.bundle_type == 'variable_quantity':
					message += '<center><table border=1 class="col-md-12" style="margin-left:250px"><tr class="alert-info" ><th>Product<th><th>Min Quantity<th><th>Max Quantity<th></tr>'
				for line in self.pack_id.wk_bundle_products:
					template_name = line.template_id.name
					if self.pack_id.bundle_type == 'fixed_quantity':
						quantity = line.product_quantity
						message += '<tr><td>   %s <td><td> %s <td></tr>'%(template_name,quantity)
					if self.pack_id.bundle_type == 'variable_quantity':
						min_quantity = line.min_bundle_qty
						max_quantity = line.max_bundle_qty
						message += '<tr><td>   %s <td><td> %s <td><td> %s <td></tr>'%(template_name,min_quantity,max_quantity)
				message += '<table></center>'
		self.description = message

	@api.onchange('pack_id')
	def onchange_pack_id(self):
		message = ''
		if self.pack_id:
			if self.product_lines:
				self.product_lines = [[5]]

	def add_product_button(self):	
		if self.product_lines:
			temp_quantity = 0
			prod_dict = {}
			order_line_selected_varinats = []
			pack_description = ''
			temp_qty = 0
			pack_qty = 0
			for product_obj in self.product_lines:
				temp_quantity = product_obj.quantity
				temp_qty = temp_qty + temp_quantity				
				if product_obj.product_id.product_tmpl_id.id in prod_dict.keys():
					temp_quantity = temp_quantity + prod_dict[product_obj.product_id.product_tmpl_id.id]
				prod_dict[product_obj.product_id.product_tmpl_id.id] = temp_quantity

			for temp_obj in self.pack_id.wk_bundle_products:
				pack_qty = pack_qty + temp_obj.product_quantity
				if temp_obj.template_id.id in prod_dict.keys():
					if prod_dict[temp_obj.template_id.id] != temp_obj.product_quantity and self.pack_id.bundle_type == 'fixed_quantity':
						self.product_lines = [(6,0,[])]
						raise ValidationError("Quantity of the Variants of %s is not equal to the Quantity in the Bundle. "%temp_obj.name)
			if self.pack_id.bundle_type == 'fixed_quantity' and  temp_qty != pack_qty:
				self.product_lines = [(6,0,[])]
				raise ValidationError("Quantity of the Variants selected is not same as the Quantity Of the Bundle.")
			for tmp_line in self.product_lines:
					order_line_variant_data = {}
					bundle_id = self.pack_id.wk_bundle_products.filtered(lambda bundle: bundle.template_id.id == tmp_line.product_id.product_tmpl_id.id)
					if bundle_id and self.pack_id.bundle_type == 'variable_quantity' and bundle_id.min_bundle_qty > 0 and bundle_id.max_bundle_qty >0 and (tmp_line.quantity < bundle_id.min_bundle_qty or tmp_line.quantity > bundle_id.max_bundle_qty):
						raise ValidationError("Please add the proper min and max quantity of the %s"%tmp_line.product_id.name)
					order_line_variant_data['variant_id'] = tmp_line.product_id.id
					order_line_variant_data['quantity_in_pack'] = tmp_line.quantity
					pack_description += '%s::Qty=%s\n'%(tmp_line.product_id.display_name, tmp_line.quantity)
					order_line_selected_varinats.append((0,0,order_line_variant_data))
			for pack_varinat in self.pack_id.product_variant_ids:
				final_description = '%s\n%s'%(pack_varinat.name,pack_description)
				sale_order = self.env['sale.order'].browse(self._context['active_id'])
				pack_price_with_discount = pack_varinat._get_combination_info_variant(pricelist=sale_order.pricelist_id)
				self.env['sale.order.line'].create({'order_id':self._context['active_id'],'product_id':pack_varinat.id,'name':pack_varinat.name, 'price_unit':pack_price_with_discount['price'],'product_uom':self.pack_id.uom_po_id.id,'product_uom_qty':1, 'wk_product_variants':order_line_selected_varinats,'name':final_description})
		else:
			self.product_lines = [(6,0,[])]
			raise ValidationError("Please select the Variants in this Bundle")


class PackTemplateLines(models.TransientModel):
	_name = 'pack.template.lines'
	_description= "Bundle Template Lines"

	bundle_product_wizard_id =  fields.Many2one('product.bundle.wizard', 'Product Pack')
	template_id = fields.Many2one('product.template', 'Product Templates')
	quantity = fields.Integer('Quantity', default=1)

class PackProductLines(models.TransientModel):
	_name = 'pack.product.lines'
	_description = "Bundle Product Lines"

	bundle_product_wizard_id =  fields.Many2one('product.bundle.wizard', 'Product Pack')
	product_id = fields.Many2one('product.product', 'Select Variants', required=True)
	quantity = fields.Integer('Quantity',required=True , default=1)

	@api.onchange('product_id')
	@api.depends('product_id')
	def change_product_lines(self):
		template_lines = []
		variant_ids_list = []
		result = {}
		if self._context.get('pack_id'):
			template_obj = self.env["product.template"].browse(self._context.get('pack_id'))
			for line in template_obj.wk_bundle_products:
				line_data = {}
				line_data['template_id'] = line.template_id.id
				line_data['quantity'] = line.product_quantity
				template_lines.append((0,0,line_data)) # creates the template lines for one2many field..
				if line.add_variants == 'selected':
					if line.varinats:
						for variant_id in line.varinats:
							variant_ids_list.append(variant_id.id)
				else:
					if line.template_id.product_variant_ids:
						for variant_id in line.template_id.product_variant_ids:
							variant_ids_list.append(variant_id.id)
			result['domain'] = {'product_id': [('id','in',variant_ids_list)]}
			return result
			