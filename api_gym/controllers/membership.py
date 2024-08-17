from odoo.http import request

from odoo import http

import datetime
format = '%d-%m-%Y'

class MemberShip(http.Controller):

    @http.route('/api/retrieve_classes', type="json", auth="public")
    def retrieve_classes(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        product_temp = []
        if  'date' not in kwargs:
            return  {"status": "failed", "massage": " Date  not Found"}
        date  = datetime.datetime.strptime(kwargs['date'], format)
        day =date.strftime("%A")


        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_no =date.weekday()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>.", day, date,day_no)

        for rec in request.env['resource.calendar.attendance'].sudo().search([('dayofweek','=',day_no),('calendar_id.is_member', '=', True)]):
            # attendance_ids = request.env['member.attendance'].sudo()\
            #     .search([('class_id','=',rec.id)])
            attendance_ids = request.env['member.attendance'].sudo() \
                .search([('class_id', '=', rec.calendar_id.id), ('date', '=', date.date())])
            product_temp.append({'id': rec.id,
                                 'name': rec.display_name,
                                 'day_of_week': days[int(rec.dayofweek)],
                                 'from': '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.hour_from * 60, 60)),
                                 'to':  '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.hour_to * 60, 60)),
                                 "trainer_id":rec.calendar_id.trainer_id.name if rec.calendar_id.trainer_id else '',
                                 'limit_of_class':rec.limit_of_class,
                                 'description':rec.description if rec.description else '',
                                 "attendance":len(attendance_ids)
                                 })

        return {"status": "success", "data": product_temp}

    @http.route('/api/retrieve_remaining_of_session', type="json", auth="public")
    def retrieve_remaining_of_session(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        if 'membership_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " MemberShip  not Found"}
        if not request.env['memberships.member'].sudo().search([('id', '=', kwargs['membership_id'])]):
            return {"status": "failed", "massage": "There 's no member ship have this id"}

        return {"status": "success", "remaining_session": request.env['memberships.member'].sudo().search(
            [('id', '=', kwargs['membership_id'])]).remaining_of_session}

    @http.route('/api/retrieve_member_ship_for_member', type="json", auth="public")
    def retrieve_membership_for_memeber(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        product_temp = []
        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}

        if not request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])]):
            return {"status": "failed", "massage": "There 's no member  have this id"}

        for rec in request.env['memberships.member'].sudo().search([('gym_member_id', '=', kwargs['member_id'])]):
            product_temp.append({'member_id': kwargs['member_id'],
                                 'name':rec.name,
                                 'member_ship_id': rec.gym_membership_type_id.id,
                                 'member_ship_name': rec.gym_membership_type_id.name,
                                 'duration_id': rec.duration_id.name,
                                 'net_amount': rec.net_amount,
                                 'start_date': rec.start_date,
                                 'end_date': rec.end_date,
                                 'number_of_session': rec.number_of_session,
                                 "remaining_of_session": rec.remaining_of_session,

                                 })

        return {"status": "success", "data": product_temp}

    @http.route('/api/retrieve_membership_type', type="json", auth="public")
    def retrieve_membership_type(self, **kwargs):
        # if api_token and str(api_token) == str(kwargs['token']):

        product_temp = []
        for rec in request.env['product.template'].sudo().search([('is_membership', '=', True)]):

            product_temp.append({'id': rec.id, 'name': rec.display_name, 'price': rec.list_price,
                                 'category':rec.categ_id.name if rec.categ_id else '',
                                 'number_of_session': rec.number_of_session})

        return {"status": "success", "data": product_temp}

    @http.route('/api/create_membership', type="json", auth="public")
    def create_memebership(self, **kwargs):

        # if api_token and str(api_token) == str(kwargs['token']):

        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}
        if 'membership_type_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Type  not Found"}
        if not request.env['product.template'].sudo().search([('id', '=', kwargs['membership_type_id'])]):
            return {"status": "failed", "massage": "There 's no member ship have this id"}
        if not request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])]):
            return {"status": "failed", "massage": "There 's no member ship have this id"}

        membership_id = request.env['memberships.member'].sudo().create({
            'gym_member_id': kwargs['member_id'],
            'gym_membership_type_id': kwargs['membership_type_id']

        })
        membership_id.sudo().membership_type_price_get()
        membership_id.sudo().compute_session()
        return {"status": "success", "membership_id": membership_id.id}
