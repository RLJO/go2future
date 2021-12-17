# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class g2f_user_menu(models.Model):
#     _name = 'g2f_user_menu.g2f_user_menu'
#     _description = 'g2f_user_menu.g2f_user_menu'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
