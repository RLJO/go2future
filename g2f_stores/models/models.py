# -*- coding: utf-8 -*-

import io
import base64
from odoo import api, fields, models, _
from random import randrange
from PIL import Image
from odoo.exceptions import ValidationError, UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

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
                qr = "{'store_id:'" + str(obj.store_id.id)+", 'door_id':'"+str(obj.name)+", type:"+str(obj.type)+"'}"
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
                        'port_number': camera.port_number
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
        zone_ids = zone_obj.search([('store_id', '=', store_id),])
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
            i.name = i.zone_id.name + " - " + i.camera_id.name


class RaspberryPi(models.Model):
    _name = 'store.raspi'
    _description = 'RaspberryPi'

    name = fields.Char('Nombre')
    ip_add = fields.Char('Dirección IP')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    sensor_ids = fields.One2many('store.sensor', inverse_name='pi_id', string='Sensor_ids')


class StoreSensor(models.Model):
    _name = 'store.sensor'
    _description = 'PI Sensors'

    name = fields.Char(string='Nombre')
    product_weight = fields.Float(string='Peso de Productos')
    calibration_factor = fields.Float(string='Factor de Calibracion')
    dt_pin = fields.Integer(string='dt_pin')
    sck_pin = fields.Integer(string='sck pin')
    zone_id = fields.Many2one('camera.zone', string='Zona')
    pi_id = fields.Many2one('store.raspi', string='Raspberry PI')
    store_id = fields.Many2one('stock.warehouse', string='Tienda', related="pi_id.store_id", store=True)

    def get_sensor_data(self, data):
        res =[]
        for sensor in data:
            res.append({
            "sensor_id": sensor.id,
            "calibration_factor": sensor.calibration_factor,
            "dt_pin": sensor.dt_pin,
            "sck_pin": sensor.sck_pin,
            "zone": sensor.zone_id.name,
        })
        return res


class ProductStore(models.Model):
    _name = 'product.store'
    _description = 'Product in Store'

    product_id = fields.Many2one('product.product', string='Producto')
    gondola = fields.Char(string='Gondola')
    gondola_id = fields.Many2one('store.raspi', string='Gondola')
    line = fields.Char(string='Linea')
    shelf = fields.Char(string='Estante')
    shelf_id = fields.Many2one('store.sensor', string='Estante')
    ini_position = fields.Char(string='Posición Inicial')
    end_position = fields.Char(string='Posición Final')
    und_front = fields.Integer(string='Unidades Frente')
    und_fund = fields.Integer(string='Unidades Fondo')
    und_high = fields.Integer(string='Unidades Alto')
    weight_total_prod = fields.Float(string='Peso total Product', compute='_compute_total_weight')
    qty_total_prod = fields.Integer(string="Cantidad total")
    qty_available_prod = fields.Integer(string="Cantidad disponible")
    store_id = fields.Many2one('stock.warehouse', string='Tienda')

    @api.depends('ini_position')
    def _compute_total_weight(self):
        for prod in self:
            prod.weight_total_prod = prod.weight_total_prod * prod.und_front
