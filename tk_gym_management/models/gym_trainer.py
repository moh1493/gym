# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, _


class GymTrainer(models.Model):
    _inherit = 'hr.employee'
    _description = 'Gym Trainer'
    _rec_name = 'name'

    is_trainer = fields.Boolean(string='Trainer')
    private_email = fields.Char(readonly=False)

    # Private Address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    gym_member_ids = fields.One2many('res.partner', 'trainer_id', string='Member')
    member_count = fields.Integer(string='Count', compute='get_member_count')

    def gym_member(self):
        return {
            'name': _('Member'),
            'domain': [('trainer_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }

    def get_member_count(self):
        count = self.env['res.partner'].search_count([('trainer_id', '=', self.id)])
        self.member_count = count

