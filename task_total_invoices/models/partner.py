from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_invoices = fields.Monetary(string="Total Invoiced Amount",
                                     compute='_compute_invoice_stats')
    total_payments_done = fields.Monetary(string="Total Payments Done",
                                          compute='_compute_invoice_stats')
    total_payments_remaining = fields.Monetary(string="Total Payments Remaining",
                                               compute='_compute_invoice_stats' )
    total_left_credit = fields.Monetary(string="Total credit left",
                                        compute='_compute_invoice_stats')

    def _compute_invoice_stats(self):
        for line in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', line.id),
                ('state', '=', 'posted')])

            total_invoice = sum(invoices.mapped('amount_total'))
            total_remaining = sum(invoices.mapped('amount_residual'))
            total_paid = total_invoice - total_remaining
            credit_left = line.user_credit - total_remaining

            line.total_invoices = total_invoice
            line.total_payments_remaining = total_remaining
            line.total_payments_done = total_paid
            line.total_left_credit = credit_left