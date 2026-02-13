from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Sale(models.Model):
    _inherit = 'sale.order'

    outstanding_amount = fields.Monetary(string="Outstanding Amount",
                                         compute="_compute_outstanding_amount",
                                         currency_field="currency_id")

    @api.depends('partner_id')
    def _compute_outstanding_amount(self):
        for line in self:
            if not line.partner_id:
                line.outstanding_amount = 0.0
                continue
            lines = self.env['account.move.line'].search([
                ('partner_id', '=', line.partner_id.id),
                ('account_type', '=', 'asset_receivable'),
                ('parent_state', '=', 'posted'),
                ('reconciled', '=', False),
            ])

            line.outstanding_amount = sum(lines.mapped('amount_residual'))

    @api.onchange('partner_id', 'order_line')
    def _onchange_check_credit_limit(self):
        for line in self:
            if line.partner_id and line.partner_id.user_credit > 0:
                current_debt = line.outstanding_amount
                new_total = current_debt + line.amount_total
                limit = line.partner_id.user_credit

                if new_total > limit:
                    return {
                        'warning': {
                            'title': "Credit Limit Warning",
                            'message': f"{line.partner_id.name}! You exceeded Your credit limit!\n"
                                       f"This Order: {line.amount_total} exceeds your credit limit\n"
                                       f"Total debt after this order would be {new_total}.\n"
                                       f"You can save this quotation, but you will NOT be able to confirm it.\n"
                                       f"Your credit limit is {limit}.\n"
                        }
                    }

    def action_confirm(self):
        for order in self:
            if order.partner_id and order.partner_id.user_credit > 0:
                current_debt = order.partner_id.credit
                new_total = current_debt + order.amount_total
                limit = order.partner_id.user_credit

                if new_total > limit:
                    raise ValidationError(
                        f"Cannot Confirm Order! \n\n"
                        f"This customer has exceeded their credit limit of {limit}.\n"
                        f"Total debt after this order would be {new_total}.\n\n"
                        f"You can save this quotation, but you will NOT be able to confirm it.\n\n"
                        "Please request a payment or increase the credit limit."
                    )
        return super().action_confirm()


class partner(models.Model):
    _inherit = 'res.partner'

    user_credit = fields.Monetary(
        string="User Credit",
        currency_field='currency_id',
        help="Amount of credit provided to this user."
    )
