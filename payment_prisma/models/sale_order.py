# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import ValidationError
import json
import requests

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_acquirer_id = fields.Many2one('marketplace.payment.acquirer')
    site_transaction_id = fields.Char(string=_('Transaction ID'), readonly=True, store=True)
    transaction_status = fields.Char(string=_('Transaction Status'), readonly=True, store=True)

    def prisma_amount_format(self, amount):
        amount_str = str(amount)
        amount_str_split = amount_str.split('.')
        if len(amount_str_split) > 1:
            amount_formated = amount_str_split[0] + amount_str_split[1].zfill(2)
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
            response = requests.post(prisma_data['url'] + '/tokens', json=data, headers=headers)
            if response.status_code == 201:
                return response.json()
            else:
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
            response = requests.post(prisma_data['url'] + '/payments', json=data, headers=headers)
            if response.status_code == 201:
                return response.json()
            else:
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
                    self.site_transaction_id = payment_response['site_transaction_id']
                    self.transaction_status = payment_response['status']
                    res = super(SaleOrder, self).action_confirm()
                    return res
        else:
            res = super(SaleOrder, self).action_confirm()
            return res
