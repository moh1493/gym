from odoo import fields, models


class SalesOrder(models.Model):
    _inherit = "sale.order"
    is_auto = fields.Boolean(copy=False)

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            if rec.is_auto:
                for pick in rec.picking_ids:
                    if pick.state not in ('done', 'cancel'):
                        pick.sudo().action_assign()
                        pick.sudo().action_set_quantities_to_reservation()
                        pick.sudo().button_validate()
                payment = self.env['sale.advance.payment.inv'].with_context({
                    'active_model': 'sale.order',
                    'active_ids': [rec.id],
                    'active_id': rec.id,

                }).create({
                    'advance_payment_method': 'delivered'
                })
                payment.create_invoices()
                for inv in rec.invoice_ids:
                    if inv.state == 'draft':
                        inv.sudo().action_post()

        return res
