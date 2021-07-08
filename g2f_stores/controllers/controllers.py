# -*- coding: utf-8 -*-
# from odoo import http


# class G2fStores(http.Controller):
#     @http.route('/g2f_stores/g2f_stores/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g2f_stores/g2f_stores/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('g2f_stores.listing', {
#             'root': '/g2f_stores/g2f_stores',
#             'objects': http.request.env['g2f_stores.g2f_stores'].search([]),
#         })

#     @http.route('/g2f_stores/g2f_stores/objects/<model("g2f_stores.g2f_stores"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g2f_stores.object', {
#             'object': obj
#         })
