from odoo import api, fields, models


class Sale(models.Model):
    _inherit = 'sale.order'



    outstanding_amount = fields.Monetary(string="Outstanding Amount",
                                         compute="_compute_outstanding_amount",
                                         currency_field="currency_id")

    @api.depends('partner_id')
    def _compute_outstanding_amount(self):
        for line in self:
            if line.partner_id:
                    line.outstanding_amount = line.partner_id.credit
                else:
                    line.outstanding_amount = 0.0