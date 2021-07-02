# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import content_disposition

class DownloadPartnerCertificateRequst(http.Controller):

    @http.route('/l10n_ar_edi/download_partner_csr/<int:partner_id>/', type='http', auth="user")
    def download_csr(self, partner_id, **kw):
        partner = http.request.env['res.partner'].sudo().browse(partner_id)
        content = partner._l10n_ar_create_certificate_request()
        if not content:
            return http.request.not_found()
        return http.request.make_response(content, headers=[('Content-Type', 'text/plain'), ('Content-Disposition', content_disposition('request.csr'))])