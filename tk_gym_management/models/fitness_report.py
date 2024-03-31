# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
import math
from odoo.exceptions import ValidationError


class GymFitnessReport(models.Model):
    _name = 'fitness.report'
    _description = 'Gym Fitness Report'
    _rec_name = 'member_id'

    member_id = fields.Many2one('res.partner', string='Member', domain="[('is_member', '=', True)]", required=True)
    date = fields.Date(string='Date', required=True)
    age = fields.Integer(string='Age', readonly=True, store=True)
    gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string='Gender')
    height = fields.Float(string='Height')
    weight = fields.Float(string='Weight')
    bmi = fields.Float(string='BMI Index', compute='bmi_report_calculate')
    bmi_categories = fields.Selection(
        [("underweight", "Under Weight"), ("normalweight", "Normal Weight"), ("overweight", "OverWeight"),
         ("indicatesobesity", " Indicates Obesity"), ("indicatesmorbidobesity", "Indicates Morbid Obesity")],
        string="BMI Categories")
    bmr = fields.Float(string='BMR (Calories/day)', compute='bmr_report_calculate')
    neck = fields.Float(string='Neck')
    waist = fields.Float(string='Waist')
    hips = fields.Float(string='Hips')
    bfp = fields.Float(string='BFP (%)', compute='bfp_report_calculate')

    @api.onchange('member_id')
    def get_gender_and_age(self):
        for rec in self:
            if rec.member_id:
                rec.gender = rec.member_id.gender
                rec.age = rec.member_id.age

    @api.depends('height', 'waist', 'neck', 'gender')
    def bfp_report_calculate(self):
        for rec in self:
            if rec.height == 0 and rec.waist == 0 and rec.neck == 0:
                rec.bfp = 0
            else:
                if rec.waist == 0 or rec.height == 0:
                    rec.waist = 1
                    rec.height = 1
                elif rec.waist < rec.neck or rec.waist == rec.neck:
                    rec.neck = 1
                waist_neck_diff = rec.waist - rec.neck
                log_of_waist_diff = math.log10(waist_neck_diff)
                log_of_height = math.log10(rec.height)
                bfp = 0
                try:
                    if rec.gender == 'm':
                        bfp_male_lp = 1.0324 - (0.19077 * log_of_waist_diff) + \
                                      (0.15456 * log_of_height)
                        bfp = (495 / bfp_male_lp) - 450
                        rec.bfp = bfp
                    else:
                        waist_hip_neck_diff = waist_neck_diff + rec.hips
                        log_of_hip = math.log10(waist_hip_neck_diff)

                        bfp_female_lp = 1.29579 - (0.35004 * log_of_hip) \
                                        + (0.221 * log_of_height)
                        bfp = (495 / bfp_female_lp) - 450
                except ZeroDivisionError:
                    pass
                except ValueError:
                    pass
                rec.bfp = bfp

    @api.depends('height', 'weight', 'gender')
    def bmr_report_calculate(self):
        for rec in self:
            if rec.height == 0:
                rec.bmr = 0
            else:
                if rec.gender == 'm':
                    rec.bmr = 88.362 + (13.397 * rec.weight) + (4.799 * rec.height) - (5.677 * rec.age)
                else:
                    rec.bmr = 447.593 + (9.247 * rec.weight) + (3.098 * rec.height) - (4.330 * rec.age)

    @api.depends('height', 'weight', )
    def bmi_report_calculate(self):
        height_square = 0
        for rec in self:
            if rec.height == 0:
                rec.height = rec.height / 1
            else:
                height_meters = rec.height / 100
                height_square = height_meters * height_meters
            if rec.weight == 0:
                rec.bmi = rec.weight / 1
            else:
                rec.bmi = rec.weight / height_square
            if rec.bmi == 0:
                rec.bmi_categories = ''
            elif rec.bmi < 18.5:
                rec.bmi_categories = 'underweight'
            elif rec.bmi < 25:
                rec.bmi_categories = 'normalweight'
            elif rec.bmi < 30:
                rec.bmi_categories = 'overweight'
            elif rec.bmi < 40:
                rec.bmi_categories = 'indicatesobesity'
            else:
                rec.bmi_categories = 'indicatesmorbidobesity'
