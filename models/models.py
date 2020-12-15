# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class ResUserInherit(models.Model):
    _inherit = 'res.users'

    token = fields.Char(
        string='token',
    )
    
    profile = fields.Binary(
        string='Profile',
    )

    def check_attendance(self, longitude, latitude, address):
        now = datetime.now().date().strftime('%Y-%m-%d')
        attendance = self.env['attendances'].search([('date', '=', now),('user_id', '=', self.id)])
        if not attendance:
            self.env['attendances'].create({
                'user_id': self.id,
                'longitude': longitude,
                'latitude': latitude,
                'address': address,
                })
            return True
        return False


class Attendance(models.Model):
    _name = 'attendances'
    
    date_time = fields.Datetime(
        string='Date Time',
        default=fields.Datetime.now,
    )

    
    date = fields.Date(
        string='date',
        default=fields.Date.context_today,
    )
    
    
    user_id = fields.Many2one(
        string='user',
        comodel_name='res.users',
        ondelete='restrict',
    )
    
    latitude = fields.Char(
        string='latitude',
    )
    
    longitude = fields.Char(
        string='longitude',
    )
    
    address = fields.Char(
        string='address',
    )
    
    
    
    

# class face_recognition(models.Model):
#     _name = 'face_recognition.face_recognition'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
