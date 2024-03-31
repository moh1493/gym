# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import models, fields


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
    trainer_id = fields.Many2one("hr.employee", readonly=True)
    class_id = fields.Many2one("resource.calendar", readonly=True)

    def check_out_member(self):
        self.check_out = fields.datetime.today()
        member_id = self.env['memberships.member.line'].search(
            [('parent_id.gym_member_id', '=', self.member_id.id), \
             ('parent_id.start_date', '<=', self.check_in),
             ('parent_id.end_date', '>=', self.check_out),
             ('state','=','draft')], order='id asc', limit=1)

        checkin = (self.check_in + timedelta(hours=2)).hour + ((self.check_in + timedelta(hours=2)).minute / 60)
        checkout = (self.check_out + timedelta(hours=2)).hour + ((self.check_out + timedelta(hours=2)).minute / 60)

        class_id = self.env['resource.calendar.attendance'].search([('hour_from', '<=', round(checkin,2)),('hour_to', '>=', round(checkin,2)), (
        'dayofweek', '=', fields.Datetime.context_timestamp(self, self.check_in).weekday()), ('calendar_id.is_member', '=', True)],limit=1)

        if member_id:
            member_id.attend_id = self.id
            member_id.state = 'attend'
            member_id.date=self.check_out
            if class_id:
                self.class_id=member_id.class_id=class_id.calendar_id.id
                self.trainer_id=member_id.trainer_id=class_id.calendar_id.trainer_id.id if class_id.calendar_id.trainer_id else ''

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
