# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except
# -

from datetime import datetime
import logging
from odoo import models, fields

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    GENDER = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')]

    lastname = fields.Char(string='Lastname')
    birthday = fields.Date(string='Birtday')
    gender = fields.Selection(GENDER, string='Gender')

    def age(self):
        age = 0
        for record in self:
            if record.birthday:
                today = datetime.now().date()
                age_rest = (today - record.birthday)
                age = round(age_rest.days/365)
        return age

    def validate_user(self, login=''):
        """ Validate if email exist.

        Parameters:
        email: str"""

        user = self.user_ids.search([('email', 'ilike', login)])
        return user or None

    def document_exist(self, identification_type, document):
        """validate if exist document and identification_type.

        Parameters:
        identification_type: str
        document: str"""

        document = self.search([
            ('l10n_latam_identification_type_id.name', 'ilike', identification_type),
            ('vat', '=', document),
            ('active', '=', True)
        ])
        return document or None

    def search_identification_type(self, identification_type):
        """Search identification_type and return objects instance.

        Parameters:
        identification_type: str
        """

        identification_type = self.env['l10n_latam.identification.type'].search([
            ('name', 'ilike', identification_type),
            ('active', '=', True)
        ])
        return identification_type or None

    def list_identification_type(self):
        """ Return identification_type list objects instance."""

        identification_type_list = self.env['l10n_latam.identification.type'].search([
            ('active', '=', True)
        ])
        return [identification.name for identification in identification_type_list]

    def search_country_info(self, country=''):
        domain = [('name', 'ilike', country)] if country else []
        countries = []
        country = self.env['res.country'].search(domain)
        for country in country:
            countries.append({country.name: [{'state': state.name, 'code': state.code} for state in country.state_ids],
                              'code': country.code,
                              'currency': country.currency_id.name,
                              'phone_code': country.phone_code,
                              })
        return countries

