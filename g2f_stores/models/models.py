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
    camera_zone_ids = fields.One2many('store.camera', inverse_name='store_id', string='Zonas de Cámaras')
    raspi_ids = fields.One2many('store.raspi', inverse_name='store_id', string='Raspberry Pi')


class StoreDoor(models.Model):
    _name = 'store.door'
    _description = 'StoreDoor'

    name = fields.Char(string='ID Puerta')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')
    qrcode = fields.Binary(string='QR', attachment=False, store=True, readonly=True, compute='_compute_qrcode')
    code = fields.Char(string="Valor QR")

    @api.depends('store_id', 'name')
    def _compute_qrcode(self):
        if self.name:
            qr = "{'store_id:'" + str(self.store_id.id)+", 'door_id':'"+str(self.name)+"'}"
            data = io.BytesIO()
            import qrcode
            qrcode.make(qr.encode(), box_size=4).save(data, optimise=True, format='PNG')
            self.code = qr
            self.qrcode = base64.b64encode(data.getvalue()).decode()

    _sql_constraints = [('unique_store_door_name', 'UNIQUE(name, store_id)',
            "Ya existe una puerta con el mismo Código en la tienda!")]


class StoreCamera(models.Model):
    _name = 'store.camera'
    _description = 'StoreCameras'

    name = fields.Char(string="Nombre")
    ai_unit = fields.Integer(string="Unidad de AI")
    device_url = fields.Char(string="URL Dispositivo")
    port_number = fields.Integer(string="Puerto")
    store_id = fields.Many2one('stock.warehouse', string='Tienda')


class CameraZone(models.Model):
    _name = 'camera.zone'
    _description = 'Camera Zone'

    name = fields.Char(string="Nombre")
    parent_id = fields.Many2one('camera.zone', string='Zona Padre')
    camera_id = fields.Many2one('store.camera', string='Camara')
    bottom_right_x = fields.Float(string='Punto ')
    bottom_right_y = fields.Float(string='Punto ')
    bottom_left_x = fields.Float(string='Punto ')
    bottom_left_y = fields.Float(string='Punto ')
    top_right_x = fields.Float(string='Punto ')
    top_right_y = fields.Float(string='Punto ')
    top_left_x = fields.Float(string='Punto ')
    top_left_y = fields.Float(string='Punto ')
    store_id = fields.Many2one('stock.warehouse', string='Tienda')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive zones.'))


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

