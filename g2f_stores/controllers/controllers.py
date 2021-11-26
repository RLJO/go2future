# -*- coding: utf-8 -*-
from odoo import http, _
from json import dumps
import logging
_logger = logging.getLogger(__name__)


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

class StoreCameraVision(http.Controller):
    @http.route(['/store/get_cameras'], type='json', auth='public',
                methods=['GET'], website=True, csrf=False) ## Controlador que NO SE USA
    def get_cameras(self, **kw):
        method = http.request.httprequest.method
        kw = http.request.jsonrequest
        print(kw)
        store_id = kw.get('store_id')
        if type(store_id) == str:
            store_id = http.request.env['stock.warehouse'].sudo().search([('code', '=', store_id)]).id
        if method == 'GET':
            print('Listar, Obtener Productos')
            res_list = http.request.env['store.camera'].sudo().search([('id', '=', store_id)])
            #print(res_list)
            #return res_list
            #return dumps(res_list)
            # res_list = self.env['store.camera'].sudo().search([('id', '=', store_id)])

        return http.request.render('g2f_stores.store_camera_tree_view', {
            'root': '/g2f_stores/g2f_stores',
            'objects': http.request.env['store.camera'].sudo().search([]),
        })
