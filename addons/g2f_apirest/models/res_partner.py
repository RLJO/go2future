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

