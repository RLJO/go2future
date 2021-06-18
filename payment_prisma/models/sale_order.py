# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import ValidationError
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_acquirer_id = fields.Many2one('marketplace.payment.acquirer')
    site_transaction_id = fields.Char(string=_('Transaction ID'), readonly=True, store=True)
    transaction_status = fields.Char(string=_('Transaction Status'), readonly=True, store=True)
    payment_prisma_status_ids = fields.One2many(comodel_name='payment.prisma.status', inverse_name='sale_order_id', readonly=True, store=True)

    def prisma_amount_format(self, amount):
        amount_str = str(amount)
        amount_str_split = amount_str.split('.')
        if len(amount_str_split) > 1:
            if len(amount_str_split[1]) == 1:
                amount_str_split[1] += '0'
            amount_formated = amount_str_split[0] + amount_str_split[1]
        else:
            amount_formated = amount
        return int(amount_formated)

    def get_vendor_amount_by_percentage(self):
        sellers_positions = {}
        sellers = []
        position = 0
        cont_amount_marketplace = 0
        for vendor_line in self.marketplace_vendor_line:
            if vendor_line.name.id not in sellers_positions:
                sellers_positions[vendor_line.name.id] = position
                sellers.append({
                    'site_id': vendor_line.name.site_ids,
                    'installments': 1,
                    'amount': self.prisma_amount_format(round(vendor_line.total_vendor, 2))
                })
                position += 1
            else:
                sellers[sellers_positions[vendor_line.name.id]]['amount'] += self.prisma_amount_format(
                    round(vendor_line.total_vendor, 2))
            cont_amount_marketplace += self.prisma_amount_format(round(
                vendor_line.amount_commission_amount_tax_company_total, 2))
        sellers.append({
            'site_id': self.company_id.site_ids,
            'installments': 1,
            'amount': cont_amount_marketplace
        })
        return sellers

    def get_prisma_data(self):
        prisma = self.env.ref('payment_prisma.marketplace_payment_acquirer_prisma')
        if prisma and prisma.state != 'disabled':
            prisma_data = {
                'public_key': prisma.public_key,
                'private_key': prisma.private_key,
            }
            if prisma.state == 'sandbox':
                prisma_data['url'] = prisma.sandbox_url
            elif prisma.state == 'production':
                prisma_data['url'] = prisma.production_url
            return prisma_data
        return {}

    def get_prisma_payment_token(self):
        self.site_transaction_id = False
        self.transaction_status = False
        prisma_data = self.get_prisma_data()
        if prisma_data:
            partner = self.partner_id
            card = partner.payment_cards_ids.filtered(lambda c: c.state == 'active')
            if not card:
                raise ValidationError(_('The customer don\'t have a card active'))
            headers = {
                'apikey': prisma_data['public_key'],
                'content-type': 'application/json',
                'cache-control': 'no-cache'
            }
            data = {
                'card_number': card.card_number,
                'card_expiration_month': card.expiration_month,
                'card_expiration_year': card.expiration_year[-2:],
                'security_code': card.security_code,
                'card_holder_name': partner.name,
                'card_holder_identification': {
                    'type': partner.l10n_latam_identification_type_id.name,
                    'number': partner.vat
                }
            }
            try:
                response = requests.post(prisma_data['url'] + '/tokens', json=data, headers=headers)
            except Exception as e:
                _logger.warning(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
                raise ValidationError(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
            if response.status_code == 201:
                _logger.warning(_('Token generado exitosamente'))
                return response.json()
            else:
                _logger.warning(_('Código de error %s, %s') % (response.status_code, response.text))
                self.site_transaction_id = response.text
                self.transaction_status = response.status_code
        return False

    def send_payment_prisma(self, token):
        prisma_data = self.get_prisma_data()
        if prisma_data:
            sellers = self.get_vendor_amount_by_percentage()
            partner = self.partner_id
            card = partner.payment_cards_ids.filtered(lambda c: c.state == 'active')
            if not card:
                raise ValidationError(_('The customer don\'t have a card active'))
            headers = {
                'apikey': prisma_data['private_key'],
                'content-type': 'application/json',
                'cache-control': 'no-cache'
            }
            data = {
                'site_transaction_id': token['id'],
                'token': token['id'],
                'payment_method_id': card.card_identification.payment_method_id,
                'bin': token['bin'],
                'amount': self.prisma_amount_format(self.amount_total),
                'currency': 'ARS',
                'installments': 1,
                'description': '',
                'payment_type': 'distributed',
                'sub_payments': sellers
            }
            try:
                response = requests.post(prisma_data['url'] + '/payments', json=data, headers=headers)
            except Exception as e:
                _logger.warning(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
                raise ValidationError(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
            if response.status_code == 201:
                _logger.warning(_('Envio de datos de pago satisfactorio'))
                return response.json()
            else:
                _logger.warning(_('Código de error %s, %s') % (response.status_code, response.text))
                self.site_transaction_id = response.text
                self.transaction_status = response.status_code
        return False

    def action_confirm(self):
        payment_acquirer_id = self.env.ref('payment_prisma.marketplace_payment_acquirer_prisma')
        if payment_acquirer_id.name == 'Prisma':
            self.payment_acquirer_id = payment_acquirer_id.id
            payment_token = self.get_prisma_payment_token()
            if payment_token:
                payment_response = self.send_payment_prisma(payment_token)
                if payment_response:
                    data = self.get_payment_data(payment_response)
                    self.env['payment.prisma.status'].create(data)
                    res = super(SaleOrder, self).action_confirm()
                    return res
        else:
            res = super(SaleOrder, self).action_confirm()
            return res

    def get_payment_data(self, response):
        data = {
            'sale_order_id': self.ids[0],
            'prisma_id': response['id'],
            'site_transaction_id': response['site_transaction_id'],
            'payment_method_id': response['payment_method_id'],
            'card_brand': response['card_brand'],
            'amount': response['amount'] / 100,
            'currency': response['currency'],
            'status': response['status'],
            'sd_ticket': response['status_details']['ticket'] if response['status_details']['ticket'] else '',
            'sd_card_authorization_code': response['status_details']['card_authorization_code'] if response['status_details']['card_authorization_code'] else '',
            'sd_address_validation_code': response['status_details']['address_validation_code'] if response['status_details']['address_validation_code'] else '',
            'sd_error': response['status_details']['error'] if response['status_details']['error'] else '',
            'date': response['date'].replace('T', ' ').replace('Z', ''),
            'customer': response['customer'] if response['customer'] else '',
            'bin': response['bin'],
            'installments': response['installments'] if response['installments'] else '',
            'payment_type': response['payment_type'],
            'site_id': response['site_id'],
            'fraud_detection': response['fraud_detection'] if response['fraud_detection'] else '',
            'aggregate_data': response['aggregate_data'] if response['aggregate_data'] else '',
            'establishment_name': response['establishment_name'] if response['establishment_name'] else '',
            'spv': response['spv'] if response['spv'] else '',
            'confirmed': response['confirmed'] if response['confirmed'] else '',
            'pan': response['pan'],
            'customer_token': response['customer_token'] if response['customer_token'] else '',
            'card_data': response['card_data'],
            'token': response['token']
        }
        if response['first_installment_expiration_date']:
            data['first_installment_expiration_date'] = response['first_installment_expiration_date'].replace('T',' ').replace('Z', '')
        subpayment_list = []
        for subpayment in response['sub_payments']:
            subpayment['amount'] = subpayment['amount'] / 100
            subpayment_list.append((0, 0, subpayment))
        if subpayment_list:
            data['sub_payments_ids'] = subpayment_list
        return data

    def update_payment(self):
        prisma_data = self.get_prisma_data()
        if prisma_data:
            headers = {
                'apikey': prisma_data['private_key'],
                'content-type': 'application/json',
                'cache-control': 'no-cache'
            }
            for status in self.payment_prisma_status_ids:
                payment_id = status.prisma_id
                payment_prisma_status_obj = status
                for line in status.sub_payments_ids:
                    line.unlink()
            if payment_id:
                try:
                    response = requests.get(prisma_data['url'] + '/payments/' + payment_id, headers=headers)
                except Exception as e:
                    _logger.warning(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
                    raise ValidationError(_('Se encontro el siguiente error al intentar procesar la solicitud:\n%s') % (e))
                self.site_transaction_id = ''
                self.transaction_status = ''
                if response.status_code == 200:
                    response = response.json()
                    _logger.warning(_('Consulta de datos de pago satisfactorio'))
                    data = self.get_payment_data(response)
                    payment_prisma_status_obj.write(data)
                else:
                    response = response.json()
                    _logger.warning(_('Código de error %s, %s') % (response.status_code, response.text))
                    self.site_transaction_id = response.text
                    self.transaction_status = response.status_code
        return True
