# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from datetime import datetime
import base64
from odoo import models, fields

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class CorporateRegistration(models.Model):
    _name = 'corporate.registration'

    GROSS_INCOME = [
        ('LOCAL', 'Opero en una sola provincia.'),
        ('SIMPLIFICADO', 'Soy un peque;o contribuyente que realiza actividades en una sola provincia.'),
        ('MULTILATERAL', 'Opero en mas de una provincia.')
    ]

    company = fields.Char(string='Company Name')
    company_cuit = fields.Char(string='Company CUIT')
    address = fields.Char(string='Company Address')
    name = fields.Char(string='Seller Name')
    last_name = fields.Char(string='Seller Last name')
    email = fields.Char()
    phone = fields.Char()
    is_exempt_iva = fields.Boolean(default=False)
    is_exclution_iva = fields.Boolean(default=False)
    is_permanent_exclution = fields.Boolean(default=False)
    certificate_date_start = fields.Date()
    certificate_date_end = fields.Date()
    certificate_file = fields.Binary(string="Certificate Exclution File",
                                     attachment=True)
    regime_gross_income = fields.Selection(GROSS_INCOME)
    registration_number_gross_income = fields.Char(
        string='registration number in gross income tax')
    registration_gross_income_file = fields.Binary(
        string="Registration Form File", attachment=True)
    industry_id = fields.Many2one('res.partner.industry', string='Sector')
    colaborate_registration = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('res.partner', string='Company')

    def create_contacts(self):
        try:
            res_partner = self.env['res.partner']

            company_id = res_partner.create({
                'name': self.company,
                'phone': self.phone,
                'company_type': 'company'
            })

            res_partner.create({
                'name': self.name,
                'phone': self.phone,
                'email': self.email,
                'company_type': 'person',
                'parent_id': company_id.id
            })

            self.colaborate_registration = True
            self.parent_id = company_id
        except Exception as error_create:
            _logger.error(error_create, error_create=error_create)
            return False, error_create

        return True

    def create_res_user(self, data):
        res_user = self.env['res.users']
        name = f"{data.get('name')} {data.get('lastname')}"
        res_user.signup({'name': name, 'login': data.get('email')})
        res_user._cr.commit()
        user = res_user.search([('login', '=', data.get('email'))])
        user.action_reset_password()
        return user.signup_url

    def create_seller(self, data):
        attachment1 = ''
        attachment2 = ''
        company = data.get('company')
        cuit = data.get('cuit')
        address = data.get('address')
        name = data.get('name')
        lastname = data.get('lastname')
        email = data.get('email')
        phone = data.get('phone')
        is_exempt_iva = True if data.get('is_exempt_iva') else False
        is_exclution_iva = True if data.get('is_exclution_iva') else False
        is_permanent_exclution = True if (data.get('is_permanent_exclution')
                                          and is_exclution_iva) else False

        certificate_date_start = None
        certificate_date_end = None
        if is_exclution_iva and not is_permanent_exclution:
            certificate_date_start = datetime.strptime(data.get(
                'certificate_date_start'), '%Y-%m-%d').date()
            certificate_date_end = datetime.strptime(data.get(
                'certificate_date_end'), '%Y-%m-%d').date()

        regime_gross_income = data.get('regime_gross_income')
        registration_number_gross_income = data.get(
            'registration_number_gross_income')
        certificate_exclution_iva_file = data.get(
            'certificate_exclution_iva_file', False)

        if certificate_exclution_iva_file:
            attachment1 = base64.encodebytes(
                certificate_exclution_iva_file.read())

        registration_gross_income_file = data.get(
            'registration_gross_income_file')

        if registration_gross_income_file:
            attachment2 = base64.encodebytes(
                registration_gross_income_file.read())

        sector_id = data.get('sector_id')
        sector_ids = self.env['res.partner.industry'].search(
            [('id', 'in', sector_id)]
        )

        try:
            self.create({
                'company': company,
                'company_cuit': cuit,
                'address': address,
                'name': name,
                'last_name': lastname,
                'email': email,
                'phone': phone,
                'is_exempt_iva': is_exempt_iva,
                'is_exclution_iva': is_exclution_iva,
                'is_permanent_exclution': is_permanent_exclution,
                'certificate_date_start': certificate_date_start,
                'certificate_date_end': certificate_date_end,
                'regime_gross_income': regime_gross_income,
                'registration_number_gross_income': registration_number_gross_income,
                'certificate_file': attachment1,
                'registration_gross_income_file': attachment2,
                'industry_id': sector_ids.id,
            })
        except Exception as error_create:
            _logger.error(error_create, error_create=error_create)
            return False, error_create

        return True, ''
