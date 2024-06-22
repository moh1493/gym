from odoo.http import request

from odoo import http

import datetime
format = '%d-%m-%Y %H:%M'

class attendance(http.Controller):
    @http.route('/api/signincancel', type="json", auth="public")
    def sign_cancel_member(self, **kwargs):
        if 'id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " id not Found"}
        membership_id = request.env['member.attendance'].sudo().search([('id','=',kwargs['id'])])
        if not membership_id:
            return {"status": "failed", "massage": " id not Found"}
        else:
            if membership_id.member_id:
                membership_id.action_cancel()
                return {"status": "sucess", "id":membership_id.id}
        return {"status": "failed", "massage": " id not Found"}

    @http.route('/api/retrieve_sign_in', type="json", auth="public")
    def retrieve_sign(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        product_temp = []
        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}
        if not request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])]):
            return {"status": "failed", "massage": "There 's no member ship have this id"}
        for rec in request.env['member.attendance'].sudo().search([('member_id', '=', kwargs['member_id'])]):
            product_temp.append( {'member_id': kwargs['member_id'],
            'class_name': rec.class_id.name,
            'class_id': rec.class_id.id,
            'check_in':rec.check_in,
             "trainer_id":rec.class_id.trainer_id.id,
             "trainer_name":rec.class_id.trainer_id.name,
                                  })

        return {"status": "success", "data": product_temp}





    @http.route('/api/signin', type="json", auth="public")
    def sign_in_member(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        product_temp = []
        if 'sign_in' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Sign in  not Found"}

        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}
        if 'class_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Class not Found"}

        if not request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])]):
            return {"status": "failed", "massage": "There 's no member ship have this id"}
        if not request.env['resource.calendar.attendance'].sudo().search([('id', '=', kwargs['class_id'])]):
            return {"status": "failed", "massage": "There isn't class have this id"}

        date = datetime.datetime.strptime(kwargs['sign_in'], format)
        class_id=request.env['resource.calendar.attendance'].sudo().search([('id', '=', kwargs['class_id'])])
        if not class_id.calendar_id.trainer_id:
            return {"status": "failed", "massage": "There isn't have Trainer"}

        membership_id = request.env['member.attendance'].sudo().create({
            'member_id': kwargs['member_id'],
            'class_id': class_id.calendar_id.id,
            'check_in':date,
             "trainer_id":class_id.calendar_id.trainer_id.id

        })
        membership_id.check_in -=datetime.timedelta(hours=3)
        membership_id.check_out_member_warning()
        if not membership_id.check_out:
            membership_id.check_out_member()




        return {"status": "success", "id": membership_id.id}

