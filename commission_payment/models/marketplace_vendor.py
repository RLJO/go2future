# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import calendar
from datetime import datetime
from odoo.exceptions import UserError, AccessError


class MarketplaceVendor(models.Model):
    _inherit = "marketplace.vendor"

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position', string='Fiscal Position',
        readonly=True,
    )

    def _commission_payment(self):
        list = []
        vendor = self.search([], order='name asc')
        today = (fields.Date.today())
        date_star = datetime.strptime("%s-%s-01 00:00:00" % (today.year, today.month-1), '%Y-%m-%d %H:%M:%S')
        date_end = "%s-%s-%s 23:59:59" % (today.year, today.month-1, calendar.monthrange(today.year, today.month-1)[1])
        date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        marketplace_vendor = vendor.filtered(lambda vendor: vendor.date >= date_star and vendor.date <= date_end
                                             and vendor.display_name != self.env.company.name)
        for vendor_id in marketplace_vendor:
            if not vendor_id.move_id and vendor_id.state == 'sale':
                a = True
                if not list == []:
                    for list_id in list:
                        if list_id['name_id'] == vendor_id.name.id:
                            list_id['amount_commission_amount_tax_company_total'] = list_id['amount_commission_amount_tax_company_total'] + vendor_id.amount_commission_amount_tax_company_total
                            list_id['id_vendor'] = list_id['id_vendor'] + ',' + str(vendor_id.id)
                            a = False
                    if a:
                        list.append({
                            'partner_id': vendor_id.name,
                            'name': vendor_id.name.name,
                            'amount_commission_amount_tax_company_total': vendor_id.amount_commission_amount_tax_company_total,
                            'currency_id': vendor_id.currency_id,
                            'id_vendor': str(vendor_id.id),
                            'date_months': vendor_id.date.strftime("%b"),
                            'name_id': vendor_id.name.id
                        })
                else:
                    list.append({
                        'partner_id': vendor_id.name,
                        'name': vendor_id.name.name,
                        'amount_commission_amount_tax_company_total': vendor_id.amount_commission_amount_tax_company_total,
                        'currency_id': vendor_id.currency_id,
                        'id_vendor': str(vendor_id.id),
                        'date_months': vendor_id.date.strftime("%b"),
                        'name_id': vendor_id.name.id
                    })
        if not list == []:
            for list_id in list:
                vals = self._prepare_invoice(list_id)
                move_id = self.move_id.sudo().create(vals)
                if move_id:
                    vals_line = self._prepare_invoice_line(move_id, list_id)
                    move_id.sudo().invoice_line_ids = [(0, 0, vals_line)]
                    id_vendor = list_id['id_vendor'].split(',')
                    for vendor in id_vendor:
                        self.search([('id', '=', int(vendor))]).move_id = move_id.id

    def _prepare_invoice(self, list_id):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        journal = self.env['account.journal'].search([('commission', '=', True)])
        if not journal:
            raise UserError(_('Please define an accounting commission journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = list_id['partner_id'].address_get(['invoice'])['invoice']
        invoice_vals = {
            'move_type': 'out_invoice',
            'currency_id': list_id['currency_id'],
            'invoice_user_id': self.env.user and self.env.user.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'partner_bank_id': list_id['partner_id'].bank_ids[:1].id,
            'invoice_origin': 'commission-' + list_id['date_months'],
            'invoice_line_ids': [],
            'company_id': self.env.company.id,
            'journal_id': journal.id,
        }
        return invoice_vals

    def _prepare_invoice_line(self, move_id, list_id):
        journal = self.env['account.journal'].search([('commission', '=', True)])
        product_id_template = self.env['product.template'].search([('commission', '=', True)])
        company = self.env.company
        tax_ids = product_id_template.product_variant_id.taxes_id.filtered(lambda t: t.company_id == company)
        return {
            'move_id': move_id.id,
            'name': product_id_template.product_variant_id.display_name,
            'price_unit': list_id['amount_commission_amount_tax_company_total'] or 0.0,
            'discount': 0,
            'quantity': 1,
            'product_uom_id': product_id_template.product_variant_id.uom_id.id,
            'product_id': product_id_template.product_variant_id.id,
            'tax_ids': [(6, 0, tax_ids.ids)],
            'company_id': self.env.company.id,
            'company_currency_id': self.env.company.currency_id.id,
            #'journal': journal.id
        }
