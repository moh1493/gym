# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields,api
#from odoo.addons.website.tools import get_video_embed_code
from odoo.addons.web_editor.tools import get_video_embed_code


class GymWorkout(models.Model):
    _name = 'gym.workout'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Workout'

    _rec_name = 'name'
    avatar = fields.Binary()
    name = fields.Char(string="Name", required=True)
    trainer_id = fields.Many2one('hr.employee', string='Support Trainer', domain=[('is_trainer', '=', True)], required=True)
    workout_day_ids = fields.Many2many('workout.days', string='Workout Days')
    calories_burn = fields.Integer(string='Calories Burn')
    number_of_days = fields.Integer(string='No. of Days')
    workout_exercise_ids = fields.One2many('workout.exercise', 'gym_workout_id', string="Workout Exercises")
    color = fields.Integer(string='Color')


class WorkoutExercise(models.Model):
    _name = 'workout.exercise'
    _description = 'Workout Exercise'
    _rec_name = 'exercise_id'

    exercise_id = fields.Many2one('gym.exercise', string='Exercise')
    exercise_for_id = fields.Many2many('exercise.for', string="Exercise For")
    equipment_ids = fields.Many2many('gym.equipment', string="Equipments")
    exercise_sets = fields.Integer(string='Sets')
    sets_repeat = fields.Integer(string='Repeat')
    weight = fields.Float(string='Weight')
    gym_workout_id = fields.Many2one('gym.workout')
    color = fields.Integer(string='Color')


class WorkoutDays(models.Model):
    _name = 'workout.days'
    _description = 'Workout Days'
    _rec_name = 'workout_day'

    workout_day = fields.Selection(
        [('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
         ('Thursday', 'Thursday'), ('Friday', 'Friday'),
         ('Saturday', 'Saturday')], string='Day', required=True)
    color = fields.Integer(string='Color')


color = fields.Integer(string='Color')


class GymExerciseFor(models.Model):
    _name = 'exercise.for'
    _description = 'Gym Exercise For'

    name = fields.Char(string="Exercise For", required=True)
    color = fields.Integer(string='Color')


class GymExercise(models.Model):
    _name = 'gym.exercise'
    _description = 'Gym Exercise'
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _columns = {

        'image': fields.Binary("Image", help="This field holds the image"),

    }
    avatar = fields.Binary()
    name = fields.Char(string="Exercise Name", required=True)
    exercise_for_id = fields.Many2many('exercise.for', string="Exercise For", required=True)
    equipment_ids = fields.Many2many('gym.equipment', string="Equipments", required=True)
    instruction = fields.Html(string="Instructions")
    exercise_step_ids = fields.One2many('gym.exercise.step', 'gym_exercise_id', string="Exercise Steps")
    benefits = fields.Html(string="Benefits")
    approx_time = fields.Char(string="Average time of Exercise")
    calories_burn_per_hour = fields.Integer(string="Calories Burn")
    color = fields.Integer(string='Color')
    note_benefit = fields.Html('Note')
    note_step = fields.Html('Note')
    exercise_video = fields.Html(compute="get_video_preview", sanitize=False)
    video_url = fields.Char('Video URL',
                            help='URL of a video for showcasing your product.')
    image = fields.Binary("Image", help="This field holds the image")

    @api.depends('video_url')
    def get_video_preview(self):
        """ to get video field """
        for image in self:
            # image.exercise_video = get_video_embed_code(image.video_url)
            image.exercise_video = get_video_embed_code(image.video_url) or False




class GymExerciseStep(models.Model):
    _name = 'gym.exercise.step'
    _description = "Gym Exercise Steps"

    name = fields.Char(string="Title", required=True)
    step_image = fields.Binary(string="Image")
    gym_exercise_id = fields.Many2one('gym.exercise')
    color = fields.Integer(string='Color')
