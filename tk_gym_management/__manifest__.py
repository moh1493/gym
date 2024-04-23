# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Advanced Gym Management | Diet & Nutrion Management | Yoga Management | Fitness Management",
    'summary': """Gym Memberships, Membership Plans, Trainers, Workouts, Exercises, Diet Plans, Fitness Report (BMI | BMR | BFP), & Diet Plan Report.""",
    'description': """
        - Gym management
        - Gym Members
        - Gym Memberships
        - Gym Membership Types
        - Gym Trainer
        - Gym Exercises
        - Gym Workouts
        - Yoga Classes
        - Diet Management
        - Nutrient Management
        - Diet Members
        - Diet & Nutrients Plans
        - Fitness Reports
        - BMI Report
        - BMR Report
        - BFP Report
    """,
    'category': 'Industry',
    'version': '15.0.1.1.1',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'base',
        'mail',
        'contacts',
        'product',
        'hr',
        'account',
        'resource'
        ,'sale'
    ],
    'data': [
        # Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # Data
        'data/data.xml',
        # Views
        'views/assets.xml',
        'views/gym_membership_views.xml',
        'views/gym_membership_member_views.xml',
        'views/gym_membership_duration_views.xml',
        'views/gym_membership_category_views.xml',
        'views/gym_employee_views.xml',
        'views/gym_equipment_views.xml',
        'views/gym_exercise_for_views.xml',
        'views/gym_exercise_views.xml',
        'views/gym_member_views.xml',
        'views/gym_class_views.xml',
        'views/gym_employee_attendance_views.xml',
        'views/gym_member_attendance_views.xml',
        'views/gym_workout_views.xml',
        'views/gym_exercise_step_views.xml',
        'views/gym_fitness_report_views.xml',
        'views/gym_food_item_views.xml',
        'views/nutrient_type_views.xml',
        'views/diet_nutrient_views.xml',
        'views/diet_plan_views.xml',
        'views/meal_type_views.xml',
        'views/diet_meal_views.xml',
        'views/workout_days_views.xml',
        'views/workout_exercise_views.xml',
        'views/sequence.xml',
        'views/class_attendee_views.xml',
        'views/gym_tag_views.xml',
        'views/product_template.xml',
        'views/calender.xml',
        # Menus
        'views/menus.xml',
        # Reports
        'report/fitness_reports.xml',
        'report/diet_reports.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tk_gym_management/static/src/xml/template.xml',
            'tk_gym_management/static/src/css/lib/dashboard.css',
            'tk_gym_management/static/src/css/lib/style.css',
            'tk_gym_management/static/src/css/style.scss',
            'tk_gym_management/static/src/js/lib/apexcharts.js',
            'tk_gym_management/static/src/js/gym.js',
        ],
    },
    'images': ['static/description/gym-management.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99,
    'currency': 'USD',
}
