# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import datetime
import calendar
from odoo import models, fields, api
from datetime import date

from dateutil.relativedelta import relativedelta


class MembershipDetails(models.Model):
    _inherit = 'product.template'
    _description = 'Gym Membership Type Details'

    is_membership = fields.Boolean()
    detailed_type = fields.Selection(default='service')
    membership_duration_id = fields.Many2one('membership.duration', string="Membership Duration")
    tag_ids = fields.Many2many('gym.tag', string='Tags')
    number_of_session = fields.Integer()

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.name, rec.membership_duration_id.name)))
        return result


class MembershipDuration(models.Model):
    _name = 'membership.duration'
    _description = 'Membership Duration'

    name = fields.Char(string="Title", required=True)
    duration = fields.Integer(string="Membership Duration", required=True)

class Memeber_session(models.Model):
    _name = "memberships.member.line"
    name = fields.Char(required=True)
    attend_id = fields.Many2one("member.attendance")
    state = fields.Selection([('draft','Draft'),('attend','Attend'),('expired','Expired')],default='draft')
    parent_id = fields.Many2one("memberships.member")
    trainer_id = fields.Many2one("hr.employee", readonly=True)
    class_id = fields.Many2one("resource.calendar", readonly=True)
    date = fields.Datetime()
class MembershipsDetails(models.Model):
    _name = 'memberships.member'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Memberships  Members Details'
    _rec_name = 'gym_member_id'
    session_ids = fields.One2many("memberships.member.line","parent_id")
    gym_membership_number = fields.Char(string='', copy=False, readonly=True,
                                        default=lambda self: 'New')
    gym_member_id = fields.Many2one('res.partner', string='Member', domain=[('is_member', '=', True)], required=True)
    gym_membership_type_id = fields.Many2one('product.template', string='Membership Type', required=True)
    duration_id = fields.Many2one('membership.duration', readonly=True, store=True, string='Membership Duration')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade',
                                 readonly=True)
    price = fields.Monetary(string='Charges')
    start_date = fields.Date(string='Start Date', default=date.today(), required=True)
    duration = fields.Integer(related='duration_id.duration', string='Membership Duration')
    end_date = fields.Date(string='End Date', compute='expired_date_count')
    invoice_membership_id = fields.Many2one('account.move', string='Invoice')

    stages = fields.Selection(
        [('draft', "Draft"), ('active', "In Progress"), ('expired', "Expired"), ('renewal', 'Renew')],
        string="Stages", default='draft')
    number_of_session = fields.Integer(related='gym_membership_type_id.number_of_session',store=True)
    is_compute = fields.Boolean()
    def compute_session(self):
        for rec in range(0,self.number_of_session):
            self.is_compute=True
            self.env['memberships.member.line'].create({
                'name':"session"+str(rec+1),
                'parent_id':self.id,
                'state':'draft',


            })

    @api.depends('start_date', 'duration')
    def expired_date_count(self):
        end_date = fields.date.today()
        for rec in self:
            end_date = rec.start_date + relativedelta(months=rec.duration)
            rec.end_date = end_date

    def draft_to_active(self):
        self.stages = 'active'

    def active_to_expiry(self):
        self.stages = 'expired'
        for rec in self.session_ids:
            if rec.state =='draft':
                rec.state = 'expired'

    @api.onchange('gym_membership_type_id', 'duration_id')
    def membership_type_price_get(self):
        for rec in self:
            if rec.gym_membership_type_id:
                rec.price = rec.gym_membership_type_id.list_price
                rec.duration_id = rec.gym_membership_type_id.membership_duration_id

    @api.model
    def create(self, vals):
        rec = super(MembershipsDetails, self).create(vals)
        if vals.get('gym_membership_number', 'New') == 'New':
            rec['gym_membership_number'] = self.env['ir.sequence'].next_by_code('rest.seq.member') or 'New'
        return rec

    def action_invoice(self):
        data = {
            'product_id': self.gym_membership_type_id.product_variant_id.id,
            'quantity': 1,
            'price_unit': self.price

        }
        invoice_line = [(0, 0, data)]

        record = {
            'partner_id': self.gym_member_id.id,
            'invoice_date': date.today(),
            'invoice_line_ids': invoice_line,
            'move_type': 'out_invoice',

        }

        invoice_id = self.env['account.move'].sudo().create(record)
        self.invoice_membership_id = invoice_id.id
        return {
            'type': "ir.actions.act_window",
            'name': 'Invoice',
            'view_type': 'form',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    @api.model
    def get_gym_stats(self):
        members = self.env['res.partner'].sudo().search_count([('is_member', '=', True)])
        memberships = self.env['memberships.member'].sudo().search_count([])
        equipments = self.env['gym.equipment'].sudo().search_count([])
        workout = self.env['gym.workout'].sudo().search_count([])
        exercise = self.env['gym.exercise'].sudo().search_count([])
        classes = self.env['gym.class'].sudo().search_count([])
        daily_attendance = [self.attendance_date(), self.employee_attendance(), self.member_attendance()]
        invoice = [self.get_month_invoice_key(), self.get_month_invoice()]

        data = {
            'gym_members': members,
            'gym_memberships': memberships,
            'gym_equipments': equipments,
            'gym_workouts': workout,
            'gym_exercises': exercise,
            'gym_classes': classes,
            'get_membership': self.get_membership(),
            'invoice': invoice,
            'daily_attendance': daily_attendance,
            'membershipperson': self.membershipperson(),
        }
        return data

    def get_month_invoice(self):
        year = fields.date.today().year
        bill_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        bill = self.env['account.move'].search([])
        for data in bill:
            if data.invoice_date:
                if data.invoice_date.year == year:
                    bill_dict[data.invoice_date.strftime("%B")] = bill_dict[data.invoice_date.strftime(
                        "%B")] + data.amount_total
        return list(bill_dict.values())

    def get_month_invoice_key(self):
        year = fields.date.today().year
        bill_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        bill = self.env['account.move'].search([])
        for data in bill:
            if data.invoice_date:
                if data.invoice_date.year == year:
                    bill_dict[data.invoice_date.strftime("%B")] = bill_dict[data.invoice_date.strftime(
                        "%B")] + data.amount_total
        return list(bill_dict.keys())

    def membershipperson(self):
        membership, membership_counts, membership_counts_f, data_cat = [], [], [], []
        membership_ids = self.env['product.template'].search([('is_membership', '=', True)])
        if not membership_ids:
            data_cat = [[], []]
        for stg in membership_ids:
            membership_data = self.env['memberships.member'].search_count(
                [('gym_membership_type_id', '=', stg.id), ('gym_member_id.gender', '=', 'm')])
            membership_f = self.env['memberships.member'].search_count(
                [('gym_membership_type_id', '=', stg.id), ('gym_member_id.gender', '=', 'f')])
            membership_counts_f.append(membership_f)
            membership_counts.append(membership_data)
            membership.append(stg.name)
        data_cat = [membership, membership_counts, membership_counts_f]
        return data_cat

    def get_membership(self):
        membership, membership_counts, data_cat = [], [], []
        membership_ids = self.env['product.template'].search([('is_membership', '=', True)])
        if not membership_ids:
            data_cat = [[], []]
        for stg in membership_ids:
            membership_data = self.env['memberships.member'].search_count(
                [('gym_membership_type_id', '=', stg.id), ('stages', '=', 'active')])
            membership_counts.append(membership_data)
            membership.append(stg.name)
        data_cat = [membership, membership_counts]
        return data_cat

    def attendance_date(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        attendance = self.env['employee.attendance'].search([])
        for data in attendance:
            if data.check_in.year == year and month == data.check_in.month:
                attendance_time = data.check_in.strftime('%d') + " " + data.check_in.strftime('%h')
                day_dict[attendance_time] = day_dict[attendance_time] + 1

        return list(day_dict.keys())

    def employee_attendance(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        attendance = self.env['employee.attendance'].search([])
        for data in attendance:
            if data.check_in.year == year and month == data.check_in.month:
                attendance_time = data.check_in.strftime('%d') + " " + data.check_in.strftime('%h')
                day_dict[attendance_time] = day_dict[attendance_time] + 1

        return list(day_dict.values())

    def member_attendance(self):
        day_dict = {}
        year = fields.date.today().year
        month = fields.date.today().month
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, num_days + 1)]
        for data in days:
            day_dict[data.strftime('%d') + " " + data.strftime('%h')] = 0
        attendance = self.env['member.attendance'].search([])
        for data in attendance:
            if data.check_in.year == year and month == data.check_in.month:
                attendance_time = data.check_in.strftime('%d') + " " + data.check_in.strftime('%h')
                day_dict[attendance_time] = day_dict[attendance_time] + 1

        return list(day_dict.values())
