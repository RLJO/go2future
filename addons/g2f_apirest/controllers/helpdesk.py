# pylint: disable=broad-except

import logging
from datetime import datetime
from json import dumps

from odoo import http, _


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
_logger = logging.getLogger(__name__)


class HelpDesk(http.Controller):


    @http.route(['/helpdesk/ticket'], type='json', auth='public',
                methods=['POST'],
                website=True, csrf=False)
    def report_ticket(self, **kw):
        """Make an inquiry or report a problem from the app and create
        a ticket automatically."""

        method = http.request.httprequest.method
        kw = http.request.jsonrequest

        login = kw.get('login')
        name = kw.get('name')
        description = kw.get('description')
        phone = kw.get('phone')
        attachment = kw.get('attachment')

        user = self._validate_user(login)

        vals = {"name": name,
                "description": description,
                "partner_id": user.partner_id.id,
                "phone": phone}

        help_desk = http.request.env['helpdesk.ticket'].sudo()
        if method == 'POST' and user:
            try:
                help_desk.create(vals)
                return {"status": 201, "message": "ticket created"}
            except Exception as error:
                _logger.error(f"Error in created ticker: {str(error)}")
                return dumps({"status": "400", "message": str(error)})

        _logger.info(f"helpdesk ticket values:{vals}")
        return {"status": 400, "message": "Method not is POST or not user"}

    def _validate_user(self, login=''):
        user = http.request.env['res.users']
        return user.sudo().search([('login', '=', login)])

    def _get_data_user(self, email):
        user = http.request.env['res.users'].sudo().search(
            [('login', 'ilike', email)]
        )
        res_partner = user.partner_id.sudo().get_data_user()
        return res_partner
