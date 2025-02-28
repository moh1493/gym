# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import calendar
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


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
    state = fields.Selection([('draft', 'Draft'), ('attend', 'Attend'), ('expired', 'Expired')], default='draft')
    parent_id = fields.Many2one("memberships.member")
    trainer_id = fields.Many2one("hr.employee", readonly=True)
    class_id = fields.Many2one("resource.calendar", readonly=True)
    date = fields.Datetime()


class MembershipsDetails(models.Model):
    _name = 'memberships.member'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Memberships  Members Details'
    _rec_name = 'name'
    name = fields.Char(compute="get_name_2")
    @api.depends('gym_membership_type_id','gym_member_id')
    def get_name_2(self):
        for rec in self:
            rec.name = ''
            if rec.gym_member_id and rec.gym_membership_type_id:
                rec.name = rec.gym_membership_type_id.name+"-"+rec.gym_member_id.name
    session_ids = fields.One2many("memberships.member.line", "parent_id")
    gym_membership_number = fields.Char(string='', copy=False, readonly=True,
                                        default=lambda self: 'New')
    gym_member_id = fields.Many2one('res.partner', tracking=True, string='Member', domain=[('is_member', '=', True)],
                                    required=True)
    mobile = fields.Char(relateds='gym_member_id.mobile')
    phone = fields.Char(relateds='gym_member_id.phone')
    email = fields.Char(relateds='gym_member_id.email')
    gym_membership_type_id = fields.Many2one('product.template', string='Membership Type', required=True, tracking=True)
    duration_id = fields.Many2one('membership.duration', readonly=True, store=True, string='Membership Duration',
                                  tracking=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade',
                                 readonly=True)
    price = fields.Monetary(string='Charges', tracking=True)
    start_date = fields.Date(string='Start Date', default=date.today(), required=True)
    duration = fields.Integer(related='duration_id.duration', string='Membership Duration')
    end_date = fields.Date(string='End Date', compute='expired_date_count', tracking=True)
    extend_date = fields.Date(tracking=True)
    extend_check = fields.Boolean()
    invoice_membership_id = fields.Many2one('account.move', string='Invoice')

    stages = fields.Selection(
        [('draft', "Draft"), ('active', "In Progress"), ('expired', "Expired"), ('renewal', 'Renew')],
        string="Stages", default='draft', tracking=True)
    number_of_session = fields.Integer(related='gym_membership_type_id.number_of_session', store=True)
    is_compute = fields.Boolean()
    remaining_of_session = fields.Integer(compute='_compute_remaining_of_session')
    discount = fields.Float(tracking=True)
    net_amount = fields.Monetary(compute='_compute_net_amount')
    payment_state = fields.Selection(related='invoice_membership_id.payment_state')

    def compute_extend_date(self):
        self.extend_check = False
        print("==================",{'default_extend_date': self.end_date},)
        self.extend_date=self.end_date
        return {
            'name': ('Extend Date'),
            'res_model': 'memberships.member',
            'view_mode': 'form',
            'context': {'default_extend_date': self.end_date},
            'view_id': self.env.ref('tk_gym_management.gym_memberships_form_view_extend_date').id,
            'res_id': self.id,

            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('price', 'discount')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = 0
            rec.net_amount = round(rec.price - (rec.price * (rec.discount / 100)))

    @api.depends('gym_membership_type_id')
    def _compute_remaining_of_session(self):
        for rec in self:
            rec.remaining_of_session = 0
            if rec.gym_membership_type_id and rec.id:
                attend_id = self.env['memberships.member.line'].search(
                    [('parent_id', '=', rec.id), ('state', '=', 'attend')])
                rec.remaining_of_session = rec.gym_membership_type_id.number_of_session
                if attend_id:
                    rec.remaining_of_session -= len(attend_id)

    def compute_session(self):
        for rec in range(0, self.number_of_session):
            self.is_compute = True
            line=self.env['memberships.member.line'].create({
                'name': "session" + str(rec + 1),
                'parent_id': self.id,
                'state': 'draft',

            })
            attend_ids = self.env['member.attendance'].search(
                [('no_member', '=', True), ('member_id', '=', self.gym_member_id.id)], order='id asc')

            if attend_ids:
                line_ids = self.env['memberships.member.line'].search([('parent_id', '=', self.id)],
                                                                      limit=len(attend_ids))

                # for line in line_ids:
                li_attend_id = self.env['member.attendance'].search(
                    [('no_member', '=', True), ('member_id', '=', self.gym_member_id.id)],   limit=1)
                line.attend_id = li_attend_id.id
                line.date = li_attend_id.check_in
                line.class_id = li_attend_id.class_id.id if li_attend_id.class_id else ''
                line.trainer_id = li_attend_id.trainer_id.id if li_attend_id.trainer_id else ''
                li_attend_id.no_member = False
                li_attend_id.member_ship_id=self.id
                li_attend_id.member_ship_line_id=line.id
                line.state = 'attend'
                line.parent_id._compute_remaining_of_session()
                if line.parent_id.remaining_of_session == 0:
                    line.parent_id.stages = 'expired'


    @api.depends('start_date', 'duration', 'extend_date')
    def expired_date_count(self):
        end_date = fields.date.today()
        for rec in self:
            end_date = rec.start_date + relativedelta(months=rec.duration)
            rec.end_date = end_date
            if rec.extend_date and rec.extend_check:
                rec.end_date = rec.extend_date
                rec.stages = 'active'

    def action_confirm_extend(self):
        print(">>>>>>>>>>>>>>>>>>.", self.extend_date, )
        print(">>>>>>>>>>>>>>>>>>.", self.end_date)
        if self.extend_date < self.end_date and self.extend_date:
            raise ValidationError(_("Extend Date must be greater than end date"))
        self.extend_check = True

    # @api.constrains('extend_date')
    # def _check_extend_date(self):
    #     if self.extend_date<self.end_date and self.extend_date:
    #         raise ValidationError(_("Extend Date must be greater than end date"))
    def draft_to_active(self):
        self.stages = 'active'

    def active_to_expiry(self):
        self.stages = 'expired'
        for rec in self.session_ids:
            if rec.state == 'draft':
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

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': ('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.invoice_membership_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_invoice(self):
        data = {
            'product_id': self.gym_membership_type_id.product_variant_id.id,
            'quantity': 1,
            'price_unit': self.price,
            'discount': self.discount

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
        self.invoice_membership_id.sudo().action_post()
        # return {
        #     'type': "ir.actions.act_window",
        #     'name': 'Invoice',
        #     'view_type': 'form',
        #     'res_model': 'account.move',
        #     'res_id': invoice_id.id,
        #     'view_mode': 'form',
        #     'target': 'current'
        # }

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
