from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commission_amount = fields.Float(
        string="Commission",
        compute="_compute_commission",
        store=True
    )

    @api.depends('product_id','shutter_height','shutter_width','component_price_total','product_uom_qty')
    def _compute_commission(self):
        for line in self:
            commission = 0.0

            base_price = line.product_id.list_price if line.product_id else 0.0

            component_price = line.component_price_total or 0.0

            subtotal_before_commission = base_price + component_price

            if (
                line.product_template_id.is_shutter_product
                and line.shutter_height > 0
                and line.shutter_width > 0
            ):
                shutter_type = line.product_template_id.shutter_type_id

                rule = self.env['range.commission'].search([
                    ('shutter_type_id', '=', shutter_type.id),
                    ('min_height', '<=', line.shutter_height),
                    ('max_height', '>=', line.shutter_height),
                    ('min_width', '<=', line.shutter_width),
                    ('max_width', '>=', line.shutter_width),
                ], limit=1)

                if rule:
                    commission = (subtotal_before_commission * rule.commission_rate) / 100.0

            line.commission_amount = commission

            line.price_unit = subtotal_before_commission + commission