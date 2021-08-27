from odoo import fields, models, api


class ConfigWSDLSettings(models.Model):
    _name = 'config.wsdlsettings'
    _description = 'Description'

    name = fields.Char(string="Nombre")
    ean_emisor = fields.Char(string="EAN del Emisor")
    nombre_emisor = fields.Char(string="Company")
    subscription_key = fields.Char(string="Subscription-Key")

