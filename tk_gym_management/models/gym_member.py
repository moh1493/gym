# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import models, fields, api


class GymMember(models.Model):
    _inherit = 'res.partner'

    is_member = fields.Boolean(string='Member')
    trainer_id = fields.Many2one('hr.employee', domain=[('is_trainer', '=', True)], string='Support Trainer')
    birthdate = fields.Date(string='Birthdate', )
    age = fields.Integer(string='Age', compute='member_age')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string='Gender', required=True)
    member_report_ids = fields.One2many('fitness.report', 'member_id', string='Report')
    diet_plan_ids = fields.One2many('diet.plan', 'member_id', string='Report')
    reports_count = fields.Integer(string='Fitness Reports', compute='get_reports_count')
    diet_schedule = fields.Integer(string='Diet Plan', compute='get_diet_schedule_count')
    workout_ids = fields.Many2many('gym.workout', string='Workout Plans')



    def create_sales_order(self):
        return {
            'name': ('Create Sales Order'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'new',
            'context':{'default_partner_id':self.id,'default_is_auto':True},
            'type': 'ir.actions.act_window',
        }

    def gym_member_reports(self):
        return {
            'name': 'Reports',
            'domain': [('member_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'fitness.report',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }

    def get_reports_count(self):
        count = self.env['fitness.report'].search_count([('member_id', '=', self.id)])
        self.reports_count = count

    def gym_member_diet_schedule(self):
        return {
            'name': 'Schedule',
            'domain': [('member_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'diet.plan',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': "ir.actions.act_window"
        }

    def get_diet_schedule_count(self):
        count = self.env['diet.plan'].search_count([('member_id', '=', self.id)])
        self.diet_schedule = count

    @api.depends('birthdate')
    def member_age(self):
        today_date = datetime.date.today()
        for rec in self:
            if rec.birthdate:
                birthdate = fields.Datetime.to_datetime(rec.birthdate).date()
                age_data = int((today_date - birthdate).days / 365)
                rec.age = age_data
            else:
                rec.age = 0
