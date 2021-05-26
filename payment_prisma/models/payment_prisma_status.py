# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import ValidationError
import json
import requests

class PaymentPrismaStatus(models.Model):
    _name = 'payment.prisma.status'

    sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    prisma_id = fields.Char(string='ID')
    site_transaction_id = fields.Char(string='Transaction ID')
    payment_method_id = fields.Integer(string='Payment Method ID')
    card_brand = fields.Char(string='Card Brand')
    amount = fields.Float(string='Amount')
    currency = fields.Char(string='currency')
    status = fields.Char(string='status')
    sd_ticket = fields.Char(string='Ticket')
    sd_card_authorization_code = fields.Char(string='Card Authorization Code')
    sd_address_validation_code = fields.Char(string='Address Validation Code')
    sd_error = fields.Char(string='Error')
    date = fields.Datetime(string='Date')
    customer = fields.Char(string='Customer')
    bin = fields.Char(string='Bin')
    installments = fields.Char(string='Installments')
    first_installment_expiration_date = fields.Datetime(string='First Installment Expiration Date')
    payment_type = fields.Char(string='Payment Type')
    site_id = fields.Char(string='Site ID')
    fraud_detection = fields.Char(string='Fraud Detection')
    aggregate_data = fields.Char(string='Aggregate Data')
    establishment_name = fields.Char(string='Establishment Name')
    spv = fields.Char(string='SPV')
    confirmed = fields.Char(string='Confirmed')
    pan = fields.Char(string='PAN')
    customer_token = fields.Char(string='Customer Token')
    card_data = fields.Char(string='Card Data')
    token = fields.Char(string='Token')
    sub_payments_ids = fields.One2many(comodel_name='payment.prisma.status.line', inverse_name='payment_prisma_status_id', string='Sub Payments')

class PaymentPrismaStatusLine(models.Model):
    _name = 'payment.prisma.status.line'

    payment_prisma_status_id = fields.Many2one(comodel_name='payment.prisma.status', string='Payment Status')
    site_id = fields.Char(string='Site ID')
    installments = fields.Char(string='Installments')
    amount = fields.Float(string='Amount')
    ticket = fields.Char('Ticket')
    card_authorization_code = fields.Char(string='Card Authorization Code')
    subpayment_id = fields.Char(string='Sub Payment ID')
    status = fields.Char(string='Status')