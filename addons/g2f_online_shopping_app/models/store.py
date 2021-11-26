# pylint: disable=eval-used
# pylint: disable=eval-referenced
# pylint: disable=consider-add-field-help
# pylint: disable=broad-except

import qrcode
import logging
from odoo import models, fields

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)


class ResStore(models.Model):
    _name = 'store'
    _description = 'Store Name'

    def _default_website(self):
        """ Find the first company's website, if there is one. """
        company_id = self.env.company.id

        if self._context.get('default_company_id'):
            company_id = self._context.get('default_company_id')

        domain = [('company_id', '=', company_id)]
        return self.env['website'].search(domain, limit=1)

    name = fields.Char()
    street = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    website_id = fields.Many2one('website', string="Website",
                                 ondelete='restrict')
    active = fields.Boolean(default=True)

    def create_qr(self, store_id, door_id):
        """Create QR Code to Store.

        Parameters:
            store_id: str,
            door_id: str
        """

        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_H,
                           box_size=10,
                           border=4)
        # info = [self.id, self.name]
        # store_id = '1'
        # door_id = '1'
        data = '{"store_id": "'+store_id+'", "door_id": "'+door_id+'"}'
        qr.add_data(data)
        qr.make(fit=True)
        imagen = qr.make_image()
        imagen.save('codigo.png')
