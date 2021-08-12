# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_repr
from odoo.tools.misc import format_date, get_lang

from collections import defaultdict
from datetime import timedelta

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    electronic_invoice_type = fields.Selection(selection=[
        ('seller_api', _('API Seller')),
        ('afip', _('AFIP')),
        ('no_afip', _('No AFIP'))
    ], string=_('Invoicing Type'), force_save=True, default='afip')
    company_invoicing = fields.Boolean(string=_('¿Facturación propia?'), default=True)

    def l10n_ar_verify_on_afip(self):
        for inv in self:
            if not inv.l10n_ar_afip_auth_mode or not inv.l10n_ar_afip_auth_code:
                raise UserError(_('Please set AFIP Authorization Mode and Code to continue!'))

            issuer, receptor = (inv.commercial_partner_id, inv.company_id.partner_id) \
                if inv.move_type in ['in_invoice', 'in_refund'] else (inv.company_id.partner_id, inv.commercial_partner_id)
            issuer_vat = issuer.ensure_vat()

            receptor_identification_code = receptor.l10n_latam_identification_type_id.l10n_ar_afip_code or '99'
            receptor_id_number = (receptor_identification_code and receptor.vat or "0")

            if inv.l10n_latam_document_type_id.l10n_ar_letter in ['A', 'M'] and receptor_identification_code != '80' or not receptor_id_number:
                raise UserError(_('For type A and M documents the receiver identification is mandatory and should be VAT'))

            document_parts = self._l10n_ar_get_document_number_parts(inv.l10n_latam_document_number, inv.l10n_latam_document_type_id.code)
            if not document_parts['point_of_sale'] or not document_parts['invoice_number']:
                raise UserError(_('Point of sale and document number are required!'))
            if not inv.l10n_latam_document_type_id.code:
                raise UserError(_('No document type selected or document type is not available for validation!'))
            if not inv.invoice_date:
                raise UserError(_('Invoice Date is required!'))

            connection = self.seller_id._l10n_ar_get_connection('wscdc')
            client, auth = connection._get_client()
            response = client.service.ComprobanteConstatar(auth, {
                'CbteModo': inv.l10n_ar_afip_auth_mode,
                'CuitEmisor': issuer_vat,
                'PtoVta': document_parts['point_of_sale'],
                'CbteTipo': inv.l10n_latam_document_type_id.code,
                'CbteNro': document_parts['invoice_number'],
                'CbteFch': inv.invoice_date.strftime('%Y%m%d'),
                'ImpTotal': float_repr(inv.amount_total, precision_digits=2),
                'CodAutorizacion': inv.l10n_ar_afip_auth_code,
                'DocTipoReceptor': receptor_identification_code,
                'DocNroReceptor': receptor_id_number})
            inv.write({'l10n_ar_afip_verification_result': response.Resultado})
            if response.Observaciones or response.Errors:
                inv.message_post(body=_('AFIP authorization verification result: %s%s', response.Observaciones, response.Errors))

    def _post_data(self, soft=True):
        for rec in self.filtered(lambda x: x.l10n_latam_use_documents and (not x.name or x.name == '/')):
            if rec.move_type in ('in_receipt', 'out_receipt'):
                raise UserError(_('We do not accept the usage of document types on receipts yet. '))

        if not self._context.get('move_reverse_cancel'):
            self.env['account.move.line'].create(self._stock_account_prepare_anglo_saxon_in_lines_vals())
            self.env['account.move.line'].create(self._stock_account_prepare_anglo_saxon_out_lines_vals())

        tax_return_moves = self.filtered(lambda m: m.tax_closing_end_date)
        tax_return_moves._close_tax_entry()

        ar_invoices = self.filtered(lambda x: x.company_id.country_id.code == "AR" and x.l10n_latam_use_documents)
        for rec in ar_invoices:
            rec.l10n_ar_afip_responsibility_type_id = rec.commercial_partner_id.l10n_ar_afip_responsibility_type_id.id
            if rec.company_id.currency_id == rec.currency_id:
                l10n_ar_currency_rate = 1.0
            else:
                l10n_ar_currency_rate = rec.currency_id._convert(
                    1.0, rec.company_id.currency_id, rec.company_id, rec.invoice_date or fields.Date.today(),
                    round=False)
            rec.l10n_ar_currency_rate = l10n_ar_currency_rate

        ar_invoices._check_argentinian_invoice_taxes()

        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            future_moves.auto_post = True
            for move in future_moves:
                msg = _('This move will be posted at the accounting date: %(date)s',
                        date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in to_post:
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.context_today(self):
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s", date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(
                    _("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                elif move.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))

            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tax_tag_ids):
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        to_post.mapped('line_ids').create_analytic_lines()
        to_post.write({
            'state': 'posted',
            'posted_before': True,
        })

        for move in to_post:
            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            if move._auto_compute_invoice_reference():
                to_write = {
                    'payment_reference': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['payment_reference']}))
                move.write(to_write)

        for move in to_post:
            if move.is_sale_document() \
                    and move.journal_id.sale_activity_type_id \
                    and (move.journal_id.sale_activity_user_id or move.invoice_user_id).id not in (
            self.env.ref('base.user_root').id, False):
                move.activity_schedule(
                    date_deadline=min((date for date in move.line_ids.mapped('date_maturity') if date),
                                      default=move.date),
                    activity_type_id=move.journal_id.sale_activity_type_id.id,
                    summary=move.journal_id.sale_activity_note,
                    user_id=move.journal_id.sale_activity_user_id.id or move.invoice_user_id.id,
                )

        customer_count, supplier_count = defaultdict(int), defaultdict(int)
        for move in to_post:
            if move.is_sale_document():
                customer_count[move.partner_id] += 1
            elif move.is_purchase_document():
                supplier_count[move.partner_id] += 1
        for partner, count in customer_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        for partner, count in supplier_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        to_post.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        to_post._check_balanced()

        to_post._set_afip_service_dates()

        to_post._stock_account_anglo_saxon_reconcile_valuation()

        to_post._log_depreciation_asset()
        to_post._auto_create_asset()

        for invoice in to_post.filtered(lambda move: move.is_invoice()):
            payments = invoice.mapped('transaction_ids.payment_id')
            move_lines = payments.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable') and not line.reconciled)
            for line in move_lines:
                invoice.js_assign_outstanding_line(line.id)

        for record in to_post.filtered(lambda move: move.move_type in ['in_invoice', 'in_refund']):
            if record.extract_state == 'waiting_validation':
                values = {
                    'total': record.get_validation('total'),
                    'subtotal': record.get_validation('subtotal'),
                    'global_taxes': record.get_validation('global_taxes'),
                    'global_taxes_amount': record.get_validation('global_taxes_amount'),
                    'date': record.get_validation('date'),
                    'due_date': record.get_validation('due_date'),
                    'invoice_id': record.get_validation('invoice_id'),
                    'partner': record.get_validation('supplier'),
                    'VAT_Number': record.get_validation('VAT_Number'),
                    'currency': record.get_validation('currency'),
                    'payment_ref': record.get_validation('payment_ref'),
                    'iban': record.get_validation('iban'),
                    'SWIFT_code': record.get_validation('SWIFT_code'),
                    'merged_lines': self.env.company.extract_single_line_per_tax,
                    'invoice_lines': record.get_validation('invoice_lines')
                }
                params = {
                    'document_id': record.extract_remote_id,
                    'values': values
                }
                try:
                    self._contact_iap_extract('/iap/invoice_extract/validate', params=params)
                    record.extract_state = 'done'
                except AccessError:
                    pass
        to_post.mapped('extract_word_ids').unlink()

        edi_document_vals_list = []
        for move in to_post:
            for edi_format in move.journal_id.edi_format_ids:
                is_edi_needed = move.is_invoice(include_receipts=False) and edi_format._is_required_for_invoice(move)

                if is_edi_needed:
                    errors = edi_format._check_move_configuration(move)
                    if errors:
                        raise UserError(_("Invalid invoice configuration:\n\n%s") % '\n'.join(errors))

                    existing_edi_document = move.edi_document_ids.filtered(lambda x: x.edi_format_id == edi_format)
                    if existing_edi_document:
                        existing_edi_document.write({
                            'state': 'to_send',
                            'attachment_id': False,
                        })
                    else:
                        edi_document_vals_list.append({
                            'edi_format_id': edi_format.id,
                            'move_id': move.id,
                            'state': 'to_send',
                        })

        self.env['account.edi.document'].create(edi_document_vals_list)
        to_post.edi_document_ids._process_documents_no_web_services()

        for invoice in to_post.filtered(lambda move: move.is_invoice()):
            payments = invoice.mapped('transaction_ids.payment_id')
            move_lines = payments.line_ids.filtered(
                lambda line: line.account_internal_type in ('receivable', 'payable') and not line.reconciled)
            for line in move_lines:
                invoice.js_assign_outstanding_line(line.id)
        return to_post

    def _post(self, soft=True):
        ar_invoices = self.filtered(lambda x: x.is_invoice() and x.company_id.country_id == self.env.ref('base.ar'))
        sale_ar_invoices = ar_invoices.filtered(lambda x: x.move_type in ['out_invoice', 'out_refund'])
        sale_ar_edi_invoices = sale_ar_invoices.filtered(lambda x: x.journal_id.l10n_ar_afip_ws)

        if not sale_ar_edi_invoices:
            sale_ar_edi_invoices = sale_ar_invoices

        (ar_invoices - sale_ar_invoices)._l10n_ar_check_afip_auth_verify_required()

        validated = error_invoice = self.env['account.move']
        for inv in sale_ar_edi_invoices:

            if not inv.company_invoicing and inv.electronic_invoice_type not in ['afip']:
                validated += inv._post_data()
                continue

            if inv._is_dummy_afip_validation():
                inv._dummy_afip_validation()
                validated += inv._post_data()
                continue

            if inv.company_invoicing:
                client, auth, transport = inv.company_id._l10n_ar_get_connection(inv.journal_id.l10n_ar_afip_ws)._get_client(return_transport=True)
                inv.electronic_invoice_type = 'afip'
            else:
                client, auth, transport = inv.seller_id._l10n_ar_get_connection(inv.journal_id.l10n_ar_afip_ws)._get_client(return_transport=True)
            validated += inv._post_data()
            return_info = inv._l10n_ar_do_afip_ws_request_cae(client, auth, transport)
            if return_info:
                error_invoice = inv
                validated -= inv
                break

            if not self.env.context.get('l10n_ar_invoice_skip_commit'):
                self._cr.commit()

        if error_invoice:
            msg = _('We could not validate the invoice in AFIP') + (' "%s" %s. ' % (
                inv.partner_id.name, inv.display_name) if inv.exists() else '. ') + _(
                'This is what we get:\n%s\n\nPlease make the required corrections and try again') % (return_info)
            if validated:
                unprocess = self - validated - error_invoice
                msg = _(
                    """Some invoices where validated in AFIP but as we have an error with one invoice the batch validation was stopped

* These invoices were validated:
%(validate_invoices)s
* These invoices weren\'t validated:
%(invalide_invoices)s
""",
                    validate_invoices="\n   * ".join(validated.mapped('name')),
                    invalide_invoices="\n   * ".join([
                        _("%s: %r amount %s", item.display_name, item.partner_id.name, item.amount_total_signed) for
                        item in unprocess
                    ])
                )
            raise UserError(msg)

        return validated + (self - sale_ar_edi_invoices)._post_data()

    @api.onchange('seller_id')
    def _onchange_seller_id_account(self):
        if self.seller_id and self.seller_id.fe_journal_id:
            self.journal_id = self.seller_id.fe_journal_id