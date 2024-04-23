# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import models, fields, api
import warnings

class GymEmployeeAttendance(models.Model):
    _name = 'employee.attendance'
    _description = 'GymEmployeeAttendance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', domain=[('is_trainer', '=', True)], required=True)
    check_in = fields.Datetime(string='Check In', default=datetime.today())
    check_out = fields.Datetime(string='Check Out', readonly=True, store=True)

    def check_out_employee(self):
        self.check_out = fields.datetime.today()


class GymMemberAttendance(models.Model):
    _name = 'member.attendance'
    _rec_name = 'member_id'
    _description = 'GymMemberAttendance'

    member_id = fields.Many2one('res.partner', string='Member', domain=[('is_member', '=', True)], required=True)
    check_in = fields.Datetime(string='Check In', default=datetime.today())
    check_out = fields.Datetime(string='Check Out', readonly=True, store=True)
    trainer_id = fields.Many2one("hr.employee", required=True)
    class_id = fields.Many2one("resource.calendar", required=True, domain="[('id','in',class_ids)]")
    class_ids = fields.Many2many("resource.calendar", compute="get_class_ids")
    no_member = fields.Boolean(copy=False)
    number_of_session_no = fields.Integer(copy=False)
    @api.depends("check_in")
    def get_class_ids(self):
        for rec in self:
            rec.class_ids = []
            if rec.check_in:
                class_ids = self.env['resource.calendar.attendance'].search([(
                    'dayofweek', '=', fields.Datetime.context_timestamp(self, rec.check_in).weekday()),
                    ('calendar_id.is_member', '=', True)], )
                rec.class_ids = [(4, line.calendar_id.id) for line in class_ids]
    def send_warning(self):
        return {
            'name': (''),
            'res_model': 'member.attendance',
            'view_mode': 'form',
            'view_id': self.env.ref('tk_gym_management.member_attendance_form_view_warning').id,
            'res_id': self.id,

            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    def action_create_memmbership(self):
        return {
            'name': ('Create Membership'),
            'res_model': 'memberships.member',
            'view_mode': 'form',
             'context':{'default_gym_member_id':self.member_id.id},

            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    def check_out_member_warning(self):
        member_id = self.env['memberships.member.line'].search(
            [('parent_id.gym_member_id', '=', self.member_id.id), \
             ('parent_id.start_date', '<=', self.check_in),
             ('parent_id.end_date', '>=', self.check_out),
             ('state', '=', 'draft')], order='id asc', limit=1)
        if not member_id and self.no_member==False:

            self.number_of_session_no = len(self.search([('member_id','=',self.member_id.id),('no_member','=',True)]))

            return self.send_warning()
        else:
            self.check_out_member()
    def check_out_member(self):
        member_id = self.env['memberships.member.line'].search(
            [('parent_id.gym_member_id', '=', self.member_id.id), \
             ('parent_id.start_date', '<=', self.check_in),
             ('parent_id.end_date', '>=', self.check_out),
             ('state', '=', 'draft')], order='id asc', limit=1)
        if not member_id and self.no_member==False:

            # self.number_of_session_no = len(self.search([('member_id','=',self.member_id.id),('no_member','=',True)]))
            self.no_member = True
            # return self.send_warning()
        self.check_out = fields.datetime.today()

        checkin = (self.check_in + timedelta(hours=2)).hour + ((self.check_in + timedelta(hours=2)).minute / 60)
        checkout = (self.check_out + timedelta(hours=2)).hour + ((self.check_out + timedelta(hours=2)).minute / 60)

        class_id = self.env['resource.calendar.attendance'].search(
            [('hour_from', '<=', round(checkin, 2)), ('hour_to', '>=', round(checkin, 2)), (
                'dayofweek', '=', fields.Datetime.context_timestamp(self, self.check_in).weekday()),
             ('calendar_id.is_member', '=', True)], limit=1)

        if member_id:
            member_id.attend_id = self.id
            member_id.state = 'attend'
            member_id.date = self.check_out
            member_id.parent_id._compute_remaining_of_session()
            if member_id.parent_id.remaining_of_session == 0:
                member_id.stages = 'expired'
            if class_id and not self.class_id:
                self.class_id = member_id.class_id = class_id.calendar_id.id
                self.trainer_id = member_id.trainer_id = class_id.calendar_id.trainer_id.id if class_id.calendar_id.trainer_id else ''

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     for rec in self:
    #         member_id = self.env['memberships.member.line'].search(
    #             [('parent_id.gym_member_id', '=', rec.member_id.id), \
    #              ('parent_id.start_date','<=',rec.check_in),
    #              ('parent_id.end_date','>=',rec.check_in),
    #              ('state', '=', 'draft')], order='id asc',limit=1 )
    #         print("===========================",member_id)
    #
    #         if member_id:
    #              member_id.attend_id=rec.id
    #              member_id.state='attend'
    #     return res
