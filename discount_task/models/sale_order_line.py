from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty')
    def _compute_discount(self):

        super()._compute_discount()

        for line in self:
            if not line.product_id:
                continue

            qty = line.product_uom_qty

            if qty > 50:
                line.discount = 10.0
            elif qty >= 11:
                line.discount = 5.0
            else:
                line.discount = 0.0