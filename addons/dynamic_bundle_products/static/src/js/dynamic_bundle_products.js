$(document).ready(function() 
{
	odoo.define('dynamic_bundle_products.dynamic_bundle_products', function (require) 
	{
		"use strict";
		var ajax = require('web.ajax'); 

		$('.oe_website_sale').each(function ()
		{
			var pack_id = $("input[name='pack_id']").attr('value');
			if (pack_id == 'True')
					{
						$('#add_to_cart').hide();
						$('.css_quantity').hide();
					}
		$('.validate_pack').on('click', function(ev){
			var template_qty = 0 ;
			// var pack_quantuty = 0;
			var total_variant_qty = 0;
			var flag = true;
			var jsonObj = [];
			var validate_button = $(this);
			var pack_id  = $(this).attr('value');
			var content = ''
			var min_max = false
			var bundle_type = $(this).attr('bundle_type')
			$('.wk_modal_outer_div').each(function() {
				var $self = $(this);
				template_qty = $(this).find('.pack_template_quantity').attr('value');
				var template_name = $(this).find('.wk_modal_text').attr('name');
				var variant_quantity = 0;
				$(this).find('.pack_product_id:checked').each(function() {

					variant_quantity = variant_quantity + parseInt($(this).parent().parent().find('.pack_variant_quantity').val());
					var item = {}
					item ["variant_id"] = $(this).val();
					item ["quantity"] = $(this).parent().parent().find('.pack_variant_quantity').val();
					if (item ["quantity"] > 0)
						jsonObj.push(item);
				});
				total_variant_qty += variant_quantity;
				var min_qty = parseInt($self.find('.pack_min_quantity').attr('value'));
				var max_qty = parseInt($self.find('.pack_max_quantity').attr('value'));
				if (variant_quantity < min_qty) {
					flag = false;
					content = "Please set the proper min quantity of the product " + template_name
					min_max = true
					return false;
				}
				if (variant_quantity > max_qty) {
					flag = false;
					content = "Please set the proper Max quantity of the product " + template_name
					min_max = true
					return false;
				}
				if (bundle_type == 'variable_quantity')
				{
					if (jsonObj.length == 0 && min_max == false) {
						flag = false;
						content = "Please select at least one product"
					}
				}
				else{
					if (template_qty != variant_quantity) {
						flag = false;
						content =  "Please Choose the Proper Quantity for " + template_name
					}
				}
			});
			if (flag == true)
			{	
				ajax.jsonRpc('/add/bundle/variants', 'call', {'jsonList':jsonObj,'pack_id':pack_id}).then(function (res)
				{
					if (res !=false)
						$(location).attr('href', res);
					else
						content = "There is an error in creating the pack please try again !!!"
				});
			}
			else{
				$(validate_button).popover({
					content: content,
					title: "WARNING!!",
					placement: "top",
					trigger: 'focus',
				});
				$(validate_button).popover('show');
				setTimeout(function () {
					$('.popover').remove();
				 }, 2000);
			}
			});

		});

	});
});

