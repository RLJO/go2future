# -*- coding: utf-8 -*-
# from odoo import http


# class G2fUserMenu(http.Controller):
#     @http.route('/g2f_user_menu/g2f_user_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g2f_user_menu/g2f_user_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('g2f_user_menu.listing', {
#             'root': '/g2f_user_menu/g2f_user_menu',
#             'objects': http.request.env['g2f_user_menu.g2f_user_menu'].search([]),
#         })

#     @http.route('/g2f_user_menu/g2f_user_menu/objects/<model("g2f_user_menu.g2f_user_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g2f_user_menu.object', {
#             'object': obj
#         })
