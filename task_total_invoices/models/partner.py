from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_move_ids = fields.One2many('account.move', 'partner_id', string="Customer Moves")
    custom_payment_ids = fields.One2many('account.payment', 'partner_id', string="Customer Payments")

    total_invoices = fields.Monetary(string="Total Invoiced Amount",
                                     compute='_compute_invoice_stats',
                                     store=True)
    total_payments_done = fields.Monetary(string="Total Payments Done",
                                          compute='_compute_invoice_stats',
                                          store=True)
    total_payments_remaining = fields.Monetary(string="Total Payments Remaining",
                                               compute='_compute_invoice_stats',
                                               store=True)

    @api.depends('custom_move_ids.state','custom_move_ids.amount_total',
                 'custom_move_ids.amount_residual','custom_move_ids.move_type',
                 'custom_payment_ids.state','custom_payment_ids.amount',
                 'custom_payment_ids.payment_type')
    def _compute_invoice_stats(self):
        for partner in self:
            invoiced = 0.0
            remaining = 0.0
            paid = 0.0

            for move in partner.custom_move_ids:
                if move.state == 'posted':
                    if move.move_type == 'out_invoice':
                        invoiced += move.amount_total
                        remaining += move.amount_residual
                    elif move.move_type == 'out_refund':
                        invoiced -= move.amount_total
                        remaining -= move.amount_residual

            for payment in partner.custom_payment_ids:
                if payment.state == 'paid' and payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        paid += payment.amount
                    elif payment.payment_type == 'outbound':
                        paid -= payment.amount

            partner.total_invoices = invoiced
            partner.total_payments_remaining = remaining
            partner.total_payments_done = paid
