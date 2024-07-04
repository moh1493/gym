# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class DietPlan(models.Model):
    _name = 'diet.plan'
    _description = 'Gym Diet Plan'
    _rec_name = 'member_id'

    name = fields.Char(string='Title', required=True)
    member_id = fields.Many2one('res.partner', string='Member', required=True)
    date = fields.Date(string='Date', required=True)
    diet_meal_ids = fields.One2many('diet.meal', 'diet_plan_id', string='Diet Meals')


class DietMeal(models.Model):
    _name = 'diet.meal'
    _description = 'Gym Diet Meal'

    name = fields.Char(string='Title', required=True)
    day = fields.Selection(
        [('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
         ('thursday', 'Thursday'), ('friday', 'Friday'),
         ('saturday', 'Saturday')], string='Day', required=True)
    diet_plan_id = fields.Many2one('diet.plan', string='Diet Plan')
    breakfast_ids = fields.One2many('meal.type', 'diet_meal_id', domain=[('meal_type', '=', 'breakfast')])
    morning_snack_ids = fields.One2many('meal.type', 'diet_meal_id', domain=[('meal_type', '=', 'midmorningsnacks')])
    lunch_ids = fields.One2many('meal.type', 'diet_meal_id', domain=[('meal_type', '=', 'lunch')])
    evening_snack_ids = fields.One2many('meal.type', 'diet_meal_id', domain=[('meal_type', '=', 'evening-snacks')])
    dinner_ids = fields.One2many('meal.type', 'diet_meal_id', domain=[('meal_type', '=', 'dinner')])
    diet_nutrient_ids = fields.One2many('diet.nutrient', 'diet_meal_id', string='Nutrients')


class DietNutrients(models.Model):
    _name = 'diet.nutrient'
    _rec_name = 'nutrient_id'
    _description = 'Gym Diet Nutrient'

    nutrient_id = fields.Many2one('nutrient.type', string='Nutrient')
    value = fields.Float(string='Value')
    unit = fields.Selection([('gm', 'gm'), ('mg', 'mg')], string='Unit')
    diet_meal_id = fields.Many2one('diet.meal')


class MealType(models.Model):
    _name = 'meal.type'
    _description = 'Gym Meal Type'

    meal_type = fields.Selection([('breakfast', 'Breakfast'), ('midmorningsnacks', 'Mid Morning Snacks'),
                                  ('lunch', 'Lunch'), ('evening-snacks', 'Evening Snacks'), ('dinner', 'Dinner')],
                                 string='Meal Type')

    food_item_id = fields.Many2one('food.item', string='Food Item', required=True)
    meal_time = fields.Float(string='Time', required=True)
    qty = fields.Float(string='Intake Qty')
    unit = fields.Selection([('unit', 'Unit'), ('gm', 'gm'), ('ml', 'ml'), ('ltr', 'ltr')], string='Unit')
    diet_meal_id = fields.Many2one('diet.meal', string='Diet Meal')


class FoodItem(models.Model):
    _name = 'food.item'
    _description = 'Gym Food Item'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    food_type = fields.Selection([('vegetables', 'Vegetables'), ('fruits', 'Fruits'),
                                  ('cereals', 'Cereals'), ('tubers', 'Tubers'), ('legumes', 'Legumes'),
                                  ('Dairy', 'Dairy'), ('meat', 'Meat'), ('sweet', 'Sweet'),
                                  ('processed', 'Processed Food')], string='Food Type', required=True)
    avatar = fields.Binary()


class NutrientType(models.Model):
    _name = 'nutrient.type'
    _description = 'Gym Nutrient Type'
    _rec_name = 'name'

    name = fields.Char(string='Name')
    avatar = fields.Binary()
