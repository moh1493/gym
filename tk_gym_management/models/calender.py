import datetime

from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = "resource.calendar"
    trainer_id = fields.Many2one("hr.employee")
    is_member = fields.Boolean()
    def get_list_today(self):
        print(">>>>>>>>>>>>>>",fields.Datetime.now().date(),fields.Datetime.now().date()+datetime.timedelta(hours=24))
        return {
            'name': (''),
            'res_model': 'member.attendance',
            'view_mode': 'tree,form',
             'domain':[('class_id','=',self.id),('check_in','>=',fields.Datetime.now().date()),('check_out','<',fields.Datetime.now().date()+datetime.timedelta(hours=24))],

            'target': 'new',
            'type': 'ir.actions.act_window',
        }
class calenderLine(models.Model):
    _inherit = "resource.calendar.attendance"
    description = fields.Char()
    limit_of_class = fields.Integer()

