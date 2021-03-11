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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company = fields.Char(string='Company Name')

    def create_seller(self, data):
        res_partner = self.env['res.partner']
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        company = data.get('company')
        sector_id = data.get('sector_id')
        sector_ids = self.env['res.partner.industry'].search(
            [('id', 'in', sector_id)]
        )

        try:
            res_partner.create({
                'name': name,
                'phone': phone,
                'email': email,
                'company': company,
                'industry_id': sector_ids.id,
            })
        except Exception as error_create:
            _logger.error("{error_create}", error_create=error_create)
            return False, error_create

        print('Aqui')
        return True, ''
