# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class GymEquipment(models.Model):
    _name = 'gym.equipment'
    _description = 'Gym Equipment'
    _rec_name = 'name'

    name = fields.Char(string="Equipment Name", required=True)
    exercise_for = fields.Many2many('exercise.for', string='Exercise For')
    serial_no = fields.Char(string="Serial No.")
    cost = fields.Char(string='Cost')
    company_name = fields.Char(string='Company Name')

    avatar = fields.Binary(string="Image")
    description = fields.Html(string="Description")
    units = fields.Integer(string="Units")
    color = fields.Integer(string='Color')
