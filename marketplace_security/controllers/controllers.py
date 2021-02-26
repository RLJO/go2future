# -*- coding: utf-8 -*-
# from odoo import http


# class MarketplaceSecurity(http.Controller):
#     @http.route('/marketplace_security/marketplace_security/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/marketplace_security/marketplace_security/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('marketplace_security.listing', {
#             'root': '/marketplace_security/marketplace_security',
#             'objects': http.request.env['marketplace_security.marketplace_security'].search([]),
#         })

#     @http.route('/marketplace_security/marketplace_security/objects/<model("marketplace_security.marketplace_security"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('marketplace_security.object', {
#             'object': obj
#         })
