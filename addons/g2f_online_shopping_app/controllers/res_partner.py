# pylint: disable=broad-except

import logging
from json import dumps

from odoo import http, _
# from odoo.exceptions import ValidationError, UserError

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

_logger = logging.getLogger(__name__)

class ResPartner(http.Controller):

    @http.route(['/online_shopping_app/user/add_childs_contacts/'], 
            type='json', auth='public', methods=['POST'], website=True,
            csrf=False)
    def add_childs_contacts(self, **kw):
        """Add more contacts addresses."""

        method = http.request.httprequest.method
        params = http.request.jsonrequest

        email = params.get('login')
        name = params.get('name')
        mobile = params.get('mobile')
        phone = params.get('mobile')
        street = params.get('address')
        country = params.get('country')
        country_state = params.get('country_state')
        state_city = params.get('state_city')
        # image_1920 = params.get('image_1920')
        zip_code = params.get('zip')
        comment = params.get('comment')

        domain = [('login', '=', email)]
        user = http.request.env['res.users'].sudo().search(domain)

        country_id, state_id = \
                user.partner_id.search_country_state_by_name(
                        country, country_state
                        )

        if method == 'POST' and user.partner_id.validate_user(email):
            vals = {'type': 'delivery', 'name': name, 'street': street,
                    'city': state_city, 'state_id': state_id,
                    'zip': zip_code, 'country_id': country_id, 
                    'comment': comment, 'email': email, 'phone': phone, 
                    'mobile': mobile, 'parent_id': user.partner_id.id}

            try:
                user.partner_id.child_ids.create(vals)
                _logger.info(vals)
            except Exception as error:
                _logger.error(error)

            response = {'status': '200', 'messsage': 'OK'}
            return dumps(response)

        msg = _('User does not exist!')
        response = {'status': '400', 'messsage': msg}
        return dumps(response)
