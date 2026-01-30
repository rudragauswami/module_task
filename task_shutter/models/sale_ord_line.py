from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shutter_height = fields.Float("Shutter Height")
    shutter_width = fields.Float("Shutter Width")

    range_config_id = fields.Many2one('shutter.range.config', string="Selected Range Config")

    lock_product_id = fields.Many2one('product.product', string="Lock Product")
    stopper_product_id = fields.Many2one('product.product', string="Stopper Product")
    blade_product_id = fields.Many2one('product.product', string="Blade Product")

    blade_qty = fields.Float("Blade Quantity")
    component_price_total = fields.Float("Component Total Price")

    @api.onchange('shutter_height', 'shutter_width', 'product_id')
    def _onchange_shutter_config(self):
        """Finds the correct components based on size and calculates price."""
        for line in self:
            if not line.product_template_id.is_shutter_product:
                continue
            if not line.shutter_height or not line.shutter_width:
                continue

            shutter_type = line.product_template_id.shutter_type_id
            if not shutter_type:
                continue


            range_rule = self.env['shutter.range.config'].search([
                ('shutter_type_id', '=', shutter_type.id),
                ('min_height', '<=', line.shutter_height),
                ('max_height', '>=', line.shutter_height),
                ('min_width', '<=', line.shutter_width),
                ('max_width', '>=', line.shutter_width),
            ], limit=1)

            if not range_rule:
                # Warning: No rule found!
                line.range_config_id = False
                return {
                    'warning': {
                        'title': "Configuration Missing",
                        'message': f"No configuration found for {line.product_id.name} with dimensions {line.shutter_height}x{line.shutter_width}."
                    }
                }

            line.range_config_id = range_rule

            comp_map = self.env['shutter.component.config'].search([
                ('range_config_id', '=', range_rule.id)
            ], limit=1)

            if comp_map:
                line.lock_product_id = comp_map.lock_product_id
                line.stopper_product_id = comp_map.stopper_product_id
                line.blade_product_id = comp_map.blade_product_id

                if comp_map.blade_qty_formula:
                    local_dict = {'height': line.shutter_height, 'width': line.shutter_width}
                    try:
                        line.blade_qty = safe_eval(comp_map.blade_qty_formula, local_dict)
                    except Exception:
                        line.blade_qty = 0.0
                else:
                    line.blade_qty = 0.0

                extra_price = 0.0
                if line.lock_product_id:
                    extra_price += line.lock_product_id.list_price
                if line.stopper_product_id:
                    extra_price += line.stopper_product_id.list_price
                if line.blade_product_id:
                    extra_price += (line.blade_product_id.list_price * line.blade_qty)

                line.component_price_total = extra_price

                line.price_unit = line.product_id.list_price + extra_price

    def create(self, vals):
        return super(SaleOrderLine, self).create(vals)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # This field checks: "Do I have any shutter products in my lines?"
    has_shutter_products = fields.Boolean(
        compute="_compute_has_shutter_products",
        store=True
    )

    @api.depends('order_line.product_template_id.is_shutter_product')
    def _compute_has_shutter_products(self):
        for order in self:
            # Returns True if at least one line is a shutter product
            order.has_shutter_products = any(
                line.product_template_id.is_shutter_product for line in order.order_line
            )