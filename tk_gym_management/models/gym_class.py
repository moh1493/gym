# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields
from datetime import date


class GymClass(models.Model):
    _name = 'gym.class'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Gym Class'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    trainer_id = fields.Many2one('hr.employee', string='Trainer', domain=[('is_trainer', '=', True)], required=True)
    tag_ids = fields.Many2many('gym.tag', string='Tags')
    class_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], default='free', string='Type')
    cost = fields.Monetary(string='Charges')
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade',
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    class_attendee_ids = fields.One2many('class.attendee', 'yoga_class_id', string='Attendees')
    free_class_attendee_ids = fields.One2many('class.attendee', 'yoga_class_id', string='Attendees')


class GymClassAttendee(models.Model):
    _name = 'class.attendee'
    _description = 'Gym Class Attendee'
    _rec_name = 'member_id'

    member_id = fields.Many2one('res.partner', string='Members', domain=[('is_member', '=', True)], required=True)
    yoga_class_id = fields.Many2one('gym.class', string='Class')
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def action_invoice(self):
        data = {
            'product_id': self.env.ref('tk_gym_management.gym_yoga_classes').id,
            'name': self.yoga_class_id.name,
            'quantity': 1,
            'price_unit': self.yoga_class_id.cost
        }
        invoice_line = [(0, 0, data)]
        record = {
            'partner_id': self.member_id.id,
            'invoice_date': date.today(),
            'invoice_line_ids': invoice_line,
            'move_type': 'out_invoice',

        }
        invoice_id = self.env['account.move'].sudo().create(record)
        self.invoice_id = invoice_id.id
        return True


class GymTag(models.Model):
    _name = 'gym.tag'
    _description = 'GymTag'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
