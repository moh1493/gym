from odoo.http import request

from odoo import http
from datetime import datetime


class Move(http.Controller):
    # // new
    @http.route('/api/create_member', type="json", auth="public")
    def create_memeber(self, **kwargs):

        # if api_token and str(api_token) == str(kwargs['token']):

        if 'name' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": "Name Of Member Id not Found"}
        else:
             customer_id = request.env['res.partner'].sudo().create({
                'name': kwargs['name'],
                'phone': kwargs['phone'] if 'phone' in kwargs else '',
                'mobile': kwargs['mobile'] if 'mobile' in kwargs else '',
                'website': kwargs['website'] if 'website' in kwargs else '',
                'email': kwargs['email'] if 'email' in kwargs else '',
                'function': kwargs['job_position'] if 'job_position' in kwargs else '',
                'birthdate': datetime.strptime(kwargs['birthdate'],'%d-%m-%Y') if 'birthdate' in kwargs else '',
                'is_member': True,

             })
             return {"status": "success", "member_id": customer_id.id}

    @http.route('/api/edit_member', type="json", auth="public")
    def edit_memeber(self, **kwargs):

        # if api_token and str(api_token) == str(kwargs['token']):

        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}
        else:
            customer_id = request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])])
            if not customer_id:
                return {"status": "failed", "massage": "There 's no mamber not found"}

            customer_id.sudo().write({
                'name': kwargs['name'],
                'phone': kwargs['phone'] if 'phone' in kwargs else '',
                'mobile': kwargs['mobile'] if 'mobile' in kwargs else '',
                'website': kwargs['website'] if 'website' in kwargs else '',
                'email': kwargs['email'] if 'email' in kwargs else '',
                'function': kwargs['job_position'] if 'job_position' in kwargs else '',
                'birthdate': datetime.strptime(kwargs['birthdate'],'%d-%m-%Y') if 'birthdate' in kwargs else '',
                'is_member': True,

            })
            return {"status": "success", "member_id": customer_id.id}

    @http.route('/api/retrieve_member', type="json", auth="public")
    def retrieve_member(self, **kwargs):

        # if api_token and str(api_token) == str(kwargs['token']):

        if 'member_id' not in kwargs:
            # customer_id = request.env['res.partner'].sudo().search([("id", "=", kwargs['customer_id'])])

            return {"status": "failed", "massage": " Member Id not Found"}
        else:
            customer_id = request.env['res.partner'].sudo().search([('id', '=', kwargs['member_id'])])
            if not customer_id:
                return {"status": "failed", "massage": "There 's no mamber not found"}

            return {"status": "success", "data": {'name': customer_id.name,
                                                  'phone': customer_id.phone,
                                                  'mobile': customer_id.mobile,
                                                  'website': customer_id.website,
                                                  'email': customer_id.email,
                                                  'job_position': customer_id.function,
                                                  'birthdate': customer_id.birthdate,

                                                  }}
