# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import logging
from odoo import models, fields

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class CorporateRegistration(models.Model):
    _name = 'corporate.registration'

    name = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    company = fields.Char(string='Company Name')
    industry_id = fields.Many2one('res.partner.industry', string='Sector')
    colaborate_registration = fields.Boolean(default=False)

    def create_seller(self, data):
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        company = data.get('company')
        sector_id = data.get('sector_id')
        sector_ids = self.env['res.partner.industry'].search(
            [('id', 'in', sector_id)]
        )

        try:
            self.create({
                'name': name,
                'phone': phone,
                'email': email,
                'company': company,
                'industry_id': sector_ids.id,
                'colaborate_registration': True,
            })
        except Exception as error_create:
            _logger.error(error_create, error_create=error_create)
            return False, error_create

        print('Aqui')
        return True, ''
