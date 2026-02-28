from odoo import api, fields, models


class VolumeDiscountRule(models.Model):
    _name = 'volume.discount.rule'
    _description = 'Dynamic Volume Discount Rules'
    _order = 'min_qty desc'

    name = fields.Char(string="Rule Name", required=True)
    min_qty = fields.Float(string="Minimum Quantity", required=True)
    discount_pct = fields.Float(string="Discount (%)", required=True)
    active = fields.Boolean(string="Active", default=True)
    product_ids = fields.Many2many('product.product',string="Specific Products")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_discount(self):
        super()._compute_discount()
        rules = self.env['volume.discount.rule'].search([('active', '=', True)])

        for line in self:
            if not line.product_id:
                continue

            qty = line.product_uom_qty
            applied_discount = 0.0

            for rule in rules:
                if rule.product_ids and line.product_id not in rule.product_ids:
                    continue

                if qty >= rule.min_qty:
                    applied_discount = rule.discount_pct
                    break
            line.discount = applied_discount