from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = "resource.calendar"
    trainer_id = fields.Many2one("hr.employee")
    is_member = fields.Boolean()
