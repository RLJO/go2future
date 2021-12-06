# -*- coding: utf-8 -*-
# from odoo import http


# class G2fApibearer(http.Controller):
#     @http.route('/g2f_apibearer/g2f_apibearer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g2f_apibearer/g2f_apibearer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('g2f_apibearer.listing', {
#             'root': '/g2f_apibearer/g2f_apibearer',
#             'objects': http.request.env['g2f_apibearer.g2f_apibearer'].search([]),
#         })

#     @http.route('/g2f_apibearer/g2f_apibearer/objects/<model("g2f_apibearer.g2f_apibearer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g2f_apibearer.object', {
#             'object': obj
#         })
