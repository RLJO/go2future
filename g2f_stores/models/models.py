# -*- coding: utf-8 -*-

import io
import base64
from odoo import api, fields, models, _
from random import randrange
from PIL import Image
import json
from odoo.exceptions import ValidationError, UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code_krikos = fields.Char(string="GLN", store=True)
    direccion_local = fields.Char(string="Direccion del MiniGO")
    access_control_url = fields.Char(string="URL Control de Accessos")
    vision_url = fields.Char(string="URL Vision")
    plano_url = fields.Char(string="URL Plano")
    door_ids = fields.One2many('store.door', inverse_name='store_id', string='Puertas')
    cameras_ids = fields.One2many('store.camera', inverse_name='store_id', string='Cámaras')
    camera_zone_ids = fields.One2many('camera.zone', inverse_name='store_id', string='Zonas de Cámaras')
    raspi_ids = fields.One2many('store.raspi', inverse_name='store_id', string='Raspberry Pi')
    product_plano_ids = fields.One2many('product.store', inverse_name='store_id', string='Productos Plano')
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    store_image = fields.Binary(string='Imagen Tienda', attachment=False)
    store_image_ids = fields.One2many('stock.warehouse.image', inverse_name='store_id', string='Stock warehouse Images')
    store_stage = fields.Selection([('draft', 'Borrador'), ('confirm', 'Confirmado')], default='draft', string="Estado Tienda")
    store_plano_sav = fields.Binary(string="Archivo sav Plano", attachment=True)
    alter_vision = fields.Boolean(string="Alternativa a Vision", default=False)
    limit_person_in_store = fields.Integer(string="Limit user in Store")
    limit_group_in_store = fields.Integer(string="Limit groups in Store")
    count_person_in_store = fields.Integer(string="Count person in Store")

    def action_send_confirm(self):
        for obj in self:
            obj.store_stage = 'confirm'

    def action_send_draft(self):
        for obj in self:
            obj.store_stage = 'draft'


class StockWarehouseImage(models.Model):
    _name = 'stock.warehouse.image'
    _description = 'Stock Warehouse Images'

    store_image = fields.Binary(string='Imagen Tienda', attachment=False)
    store_id = fields.Many2one('stock.warehouse', string='Tienda')


class StoreDoor(models.Model):
    _name = 'store.door'
    _description = 'StoreDoor'

    name = fields.Char(string='ID Puerta')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    qrcode = fields.Binary(string='QR', attachment=False, store=True, readonly=True, compute='_compute_qrcode')
    code = fields.Char(string="Valor QR")
    type = fields.Selection(string="Tipo", selection=[('in', 'Entrada'), ('out', 'Salida'), ('staff', 'Staff')])
    description = fields.Char(string='Descripción')

    @api.depends('store_id', 'name', 'type')
    def _compute_qrcode(self):
        for obj in self:
            if obj.name:
                qr = "{\"store_id\":\"" + str(obj.store_id.id) + "\", \"door_id\":\"" + str(obj.name) + "\", \"type\":\"" + str(obj.type) + "\"}"
                data = io.BytesIO()
                import qrcode
                qrcode.make(qr.encode(), box_size=4).save(data, optimise=True, format='PNG')
                obj.code = qr
                obj.qrcode = base64.b64encode(data.getvalue()).decode()

    _sql_constraints = [('unique_store_door_name', 'UNIQUE(name, store_id)',
            "Ya existe una puerta con el mismo Código en la tienda!")]

    def get_door_cam(self, doors):
        result = {}
        for door in doors:
            cameras = self.env['store.camera'].search([('door_id', '=', door.id)])
            cams_url = []
            for camera in cameras:
                cams_url.append(camera.device_url)
            if cams_url:
                result[door.name] = cams_url
        return result


class StoreServer(models.Model):
    _name = 'store.iaserver'
    _description = 'IA server'

    name = fields.Char(string="Nombre")


class StoreCamera(models.Model):
    _name = 'store.camera'
    _description = 'StoreCameras'

    name = fields.Char(string="Nombre")
    ai_unit = fields.Many2one('store.iaserver', string="Unidad de AI")
    #ai_unit = fields.Integer(string="Unidad de AI")
    device_url = fields.Char(string="URL Dispositivo")
    port_number = fields.Integer(string="Puerto")
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    # zone_ids = fields.One2many('camera.zone', inverse_name='camera_id', string='Zonas')
    camera_image = fields.Binary(string='Imagen de Camara', attachment=False)
    door_active = fields.Boolean(string='¿Apunta a puerta?')
    door_id = fields.Many2one('store.door', string='Puerta')
    movement_resolution = fields.Integer(string='Resolución de Movimiento', default=-1)
    movement_threshold = fields.Integer(string='Umbral de Movimiento', default=-1)
    max_fps = fields.Integer(string='FPS Maximo', default=-1)
    crop_min_x = fields.Integer(string='Crop Mimimo X', default=-1)
    crop_max_x = fields.Integer(string='Crop Maximo X', default=-1)
    crop_min_y = fields.Integer(string='Crop Mimimo Y', default=-1)
    crop_max_y = fields.Integer(string='Crop Maximo Y', default=-1)
    rotation = fields.Boolean(string='Rotación', default=0)

    @api.onchange('door_active')
    def onchange_door_active(self):
        if not self.door_active:
            self.door_id = ''

    def get_camera_by_ai_unit(self, ai_unit):
        domain = [('ai_unit', '=', ai_unit)]
        res_list = self.env['store.camera'].search(domain)
        #_logger.info("Values: %s" % res_list)
        data = []
        if res_list:
            for camera in res_list:
                data.append(
                    {
                        'id': camera.id,
                        'camera_name': camera.name,
                        'ai_unit': camera.ai_unit.id,
                        'device_url': camera.device_url,
                        'port_number': camera.port_number,
                        'movement_resolution': camera.movement_resolution,
                        'movement_threshold': camera.movement_threshold,
                        'max_fps': camera.max_fps,
                        'rotation': camera.rotation,
                        'corp': {
                            'min_x': camera.crop_min_x,
                            'max_x': camera.crop_max_x,
                            'min_y': camera.crop_min_y,
                            'max_y': camera.crop_max_y,
                        }
                    },
                )
        return data


class CameraZone(models.Model):
    _name = 'camera.zone'
    _description = 'Camera Zone'

    name = fields.Char(string="Nombre")
    parent_id = fields.Many2one('camera.zone', string='Zona Padre')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    camera_points_ids = fields.One2many('camera.zone.points', 'zone_id', string='Camara-Puntos')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive zones.'))

    def data_zone_camera(self, store_id):
        zone_obj = self.env['camera.zone']
        if type(store_id) == str:
            store_id = self.env['stock.warehouse'].search([('code', '=', store_id)]).id

        zone_ids = zone_obj.search([('store_id', '=', store_id)])
        data = []
        for zone in zone_ids:
            if zone.parent_id: # Solo sub_zonas
                for camera in zone.camera_points_ids:
                    data.append({
                        'id': zone.id,
                        'zone_name': zone.name,
                        'bottom_right_x': camera.bottom_right_x,
                        'bottom_right_y': camera.bottom_right_y,
                        'bottom_left_x': camera.bottom_left_x,
                        'bottom_left_y': camera.bottom_left_y,
                        'top_right_x': camera.top_right_x,
                        'top_right_y': camera.top_right_y,
                        'top_left_x': camera.top_left_x,
                        'top_left_y': camera.top_left_y,
                        'parent_zone': zone.parent_id.id,
                        'camera_id': camera.camera_id.id
                    })
        return data


class ZoneCameraPoints(models.Model):
    _name = 'camera.zone.points'
    _description = 'Puntos de Zonas'

    name = fields.Char(string="Puntos", compute='name_zone_camera')
    zone_id = fields.Many2one('camera.zone', string='Zona')
    store_id = fields.Many2one('stock.warehouse', string='Tienda', related='zone_id.store_id')
    camera_id = fields.Many2one('store.camera', string='Camara')
    camera_image_zone = fields.Binary(string='Imagen de Camara', related='camera_id.camera_image', store=True)
    bottom_right_x = fields.Float(string='Punto x abajo derecho')
    bottom_right_y = fields.Float(string='Punto y abajo derecho')
    bottom_left_x = fields.Float(string='Punto x abajo izquierdo')
    bottom_left_y = fields.Float(string='Punto y abajo izquierdo')
    top_right_x = fields.Float(string='Punto x arriba derecho')
    top_right_y = fields.Float(string='Punto y arriba derecho')
    top_left_x = fields.Float(string='Punto x arriba izquierdo')
    top_left_y = fields.Float(string='Punto y arriba izquierdo')

    def name_zone_camera(self):
        for i in self:
            i.name = i.zone_id.name or "" + " - " + i.camera_id.name or ""


class RaspberryPi(models.Model):
    _name = 'store.raspi'
    _description = 'RaspberryPi'

    name = fields.Char('Nombre')
    ip_add = fields.Char('Dirección IP')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    sensor_ids = fields.One2many('store.sensor', inverse_name='pi_id', string='Sensor_ids')
    position_x = fields.Float(string='Posición X', store=True)
    position_y = fields.Float(string='Posición Y', store=True)
    rotation = fields.Integer(string="Rotación")

    def get_plano_shelf_data(self, store):
        res = []
        store_id = self.env['stock.warehouse'].search([('code', '=', store)])
        if not store_id:
            store_id = self.env['stock.warehouse'].search([('name', '=', store)])
            if not store_id:
                store_id = self.env['stock.warehouse'].search([('id', '=', store)])
        ids = self.env['store.raspi'].search([('store_id', '=', store_id.id)])
        for gond in ids:
            shelf_data = []
            res.append({
                "id": gond.id,
                "name": gond.name,
                "store_id": gond.store_id.id,
                # "store_name": gond.store_id.name,
                "store_code": gond.store_id.code,
                "x_position": gond.position_x,
                "y_position": gond.position_y,
                "rotation": gond.rotation,
                "shelf_ids": shelf_data
            })
            for shelf in gond.sensor_ids:
                shelf_data.append({
                    "shelf_id": shelf.id,
                    "shelf_name": shelf.name,
                    "z_position": shelf.position_z
                })

        return res

    def post_plano_shelf_data(self, data):
        ids_updated = []
        obj_gond = self.env['store.raspi']
        obj_shelf = self.env['store.sensor']
        for vals in data:
            id = vals.get('id')
            x_new = vals.get('x_position')
            y_new = vals.get('y_position')
            rotation = vals.get('rotation')
            gond = obj_gond.search([('id', '=', id)])
            gond.write({'position_x': x_new, 'position_y': y_new, 'rotation': rotation})
            ids_updated.append(id)
            for shelf in vals['shelf_ids']:
                s_id = shelf['shelf_id']
                z_new = shelf['z_position']
                shf = obj_shelf.search([('id', '=', s_id)])
                shf.write({'position_z': z_new})
        msg = "Actualizados: %s " % ids_updated
        res = {'status': 0, 'message': msg}
        return res


class StoreSensor(models.Model):
    _name = 'store.sensor'
    _description = 'PI Sensors'

    name = fields.Char(string='Nombre')
    product_weight = fields.Float(string='Peso de Productos')
    calibration_factor = fields.Float(string='Factor de Calibracion')
    dt_pin = fields.Integer(string='dt_pin')
    sck_pin = fields.Integer(string='sck pin')
    cart_id = fields.Integer(string='cart_id', store=True)
    zone_id = fields.Many2one('camera.zone', string='Zona')
    pi_id = fields.Many2one('store.raspi', string='Raspberry PI')
    store_id = fields.Many2one('stock.warehouse', string='Tienda', related="pi_id.store_id", store=True)
    position_z = fields.Float(string='Posición Z', store=True)

    def get_sensor_data(self, data):
        res =[]
        for sensor in data:
            res.append({
            # "sensor_id": sensor.id,
            "cart_id": sensor.name,
            "calibration_factor": sensor.calibration_factor,
            "dt_pin": sensor.dt_pin,
            "sck_pin": sensor.sck_pin,
            "zone": sensor.zone_id.name,
            # "cart_id": sensor.cart_id,
        })
        return res

    def post_sensor_calibration_data(self, sensor, c_factor):
        """ACTUALIZA el factor de calibración"""
        obj_sensor = self.env['store.sensor'].search([("name", "=", sensor)])
        if obj_sensor.id:
            obj_sensor.write({'calibration_factor': c_factor})
            return True
        else:
            return False


class ProductStore(models.Model):
    _name = 'product.store'
    _description = 'Product in Store'

    product_id = fields.Many2one('product.product', string='Producto')
    gondola_id = fields.Many2one('store.raspi', string='Gondola')
    line = fields.Integer(string='Linea')
    shelf_id = fields.Many2one('store.sensor', string='Estante')
    ini_position = fields.Integer(string='Posición Inicial')
    end_position = fields.Integer(string='Posición Final')
    und_front = fields.Integer(string='Unidades Frente')
    und_fund = fields.Integer(string='Unidades Fondo')
    und_high = fields.Integer(string='Unidades Alto')
    weight_total_prod = fields.Float(string='Peso total Product', compute='_compute_total_weight')
    qty_total_prod = fields.Integer(string="Cantidad total")
    qty_available_prod = fields.Integer(string="Cantidad disponible")
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    rotation_p = fields.Integer(string="Rotación del Producto")
    peso_bruto = fields.Integer('Gross weight (g)', related='product_id.product_tmpl_id.peso_bruto', store=True)
    weight_threshold = fields.Integer('Umbral de Peso', related='product_id.product_tmpl_id.weight_threshold', store=True)

    @api.depends('ini_position')
    def _compute_total_weight(self):
        for prod in self:
            prod.weight_total_prod = prod.product_id.peso_bruto * prod.qty_total_prod

    @api.model
    def _set_plano(self, values):
        ids_created = []
        ids_updated = []
        for vals in values:
            code = vals.get('code')
            product = vals.get('product')
            gondola = vals.get('gondola')
            linea = vals.get('linea')
            estante = vals.get('estante')
            qty_total = vals.get('qty_total')
            ini_position = vals.get('ini_position')
            end_position = vals.get('end_position')
            und_front = vals.get('und_front')
            und_fund = vals.get('und_fund')
            und_high = vals.get('und_high')
            rotation_p = vals.get('rotation')
            if qty_total <= 0:
                msg = 'El campo qty_total debe ser mayor a cero (0)'
                res = {'status': '422', 'messsage': msg}
                return res
            if und_front <= 0:
                res = {'ERROR': 'El campo und_front debe ser mayor a cero (0)'}
                return res
            if und_fund <= 0:
                res = {'ERROR': 'El campo und_fund debe ser mayor a cero (0)'}
                return res
            if und_high <= 0:
                msg = 'El campo und_high debe ser mayor a cero (0)'
                res = {'status': '422', 'messsage': msg}
                return res
            local_id = self.env['stock.warehouse'].search([('code', '=', code)])
            if not local_id:
                msg = 'No se encontró Minigo registrado con el código: %s' % code
                res = {'status': '422', 'messsage': msg}
                return res
            product_id = self.env['product.product'].search([('barcode', '=', product)])
            if not product_id:
                msg = 'No se encontró Producto registrado con el código EAN13: %s' % product
                res = {'status': '422', 'messsage': msg}
                return res
            product_plano_ids = local_id.product_plano_ids.filtered(lambda p: p.product_id.barcode == product and
                                                                              p.store_id.code == code)
            # nota: no se puede filtrar por estos valores si se  cambian en la aplicacion de plano
            # p.gondola_id.name == gondola and # p.shelf_id == estante and
            if not product_plano_ids:
                action_flag = 'c'
            else:
                action_flag = 'w'
            gondola_id = self.env['store.raspi'].search([('name', 'like', gondola)])
            if not gondola_id:
                msg = 'No se encontró Góndola registrada con el nombre: %s' % gondola
                res = {'status': '422', 'messsage': msg}
                return res
            shelf_id = self.env['store.sensor'].search([('id', '=', estante)])
            if not shelf_id:
                msg = 'No se encontró Estante registrado con el nombre: %s' % estante
                res = {'status': '422', 'messsage': msg}
                return res

            data = {
                'gondola_id': gondola_id.id,
                'line': linea,
                'shelf_id': shelf_id.id,
                'qty_total_prod': qty_total,
                'ini_position': ini_position,
                'end_position': end_position,
                'und_front': und_front,
                'und_fund': und_fund,
                'und_high': und_high,
                'rotation': rotation_p,
            }
            if action_flag == 'c':
                data['product_id'] = product_id.id
                data['store_id'] = local_id.id
                new = product_plano_ids.create(data)
                ids_created.append(new.id)
            if action_flag == 'w':
                product_plano_ids.write(data)
                ids_updated.append(product_plano_ids.id)
        msg = 'Creados: %s, Actualizados: %s' % (ids_created, ids_updated)
        res = {'status': 200, 'messsage': msg}
        return res

    @api.model
    def _get_plano(self, store):
        store_id = self.env['stock.warehouse'].search([('code', '=', store)]).id
        product_list = self.env['product.store'].search([('store_id', '=', store_id)])
        data = []
        for prod in product_list:
            data.append(
                {
                    'product': prod.product_id.barcode,
                    'gondola_id': prod.gondola_id.name,
                    'line': prod.line,
                    'shelf_id': prod.shelf_id.id,
                    'qty_total_prod': prod.qty_total_prod,
                    'ini_position': prod.ini_position,
                    'end_position': prod.end_position,
                    'und_front': prod.und_front,
                    'und_fund': prod.und_fund,
                    'und_high': prod.und_high,
                    'rotation': prod.rotation_p,
                }
            )
        return data

