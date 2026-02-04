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

    allowed_lock_ids = fields.Many2many('product.product', relation='rel_line_allowed_locks',
                                        compute='_compute_allowed_components')
    allowed_stopper_ids = fields.Many2many('product.product', relation='rel_line_allowed_stoppers',
                                           compute='_compute_allowed_components')
    allowed_blade_ids = fields.Many2many('product.product', relation='rel_line_allowed_blades',
                                         compute='_compute_allowed_components')


    @api.constrains('shutter_height', 'shutter_width')
    def _check_shutter_dimensions(self):
        for line in self:
            # 1. Skip if not a shutter product
            if not line.product_template_id.is_shutter_product:
                continue

            h = line.shutter_height
            w = line.shutter_width

            if h == 0 and w == 0:
                raise ValidationError("Missing Shutter Height and Shutter Width!")

            if h > 0 and w <= 0:
                raise ValidationError(f"Missing Width! Please enter the Shutter Width for '{line.name}'.")

            if w > 0 and h <= 0:
                raise ValidationError(f"Missing Height! Please enter the Shutter Height for '{line.name}'.")

            shutter_type = line.product_template_id.shutter_type_id
            range_rule = self.env['shutter.range.config'].search([
                ('shutter_type_id', '=', shutter_type.id),
                ('min_height', '<=', h),
                ('max_height', '>=', h),
                ('min_width', '<=', w),
                ('max_width', '>=', w),
            ], limit=1)

            if not range_rule:
                raise ValidationError(
                    f"Configuration Not Found!\n"
                    f"We cannot manufacture a shutter of size {h} x {w}.\n"
                    f"Please check the Shutter Range Rules."
                )

    @api.depends('shutter_height', 'shutter_width', 'product_id')
    @api.onchange('shutter_height', 'shutter_width', 'product_id')
    def _compute_allowed_components(self):
        for line in self:
            line.allowed_lock_ids = False
            line.allowed_stopper_ids = False
            line.allowed_blade_ids = False

            if not line.product_template_id.is_shutter_product:
                line.range_config_id = False
                continue

            if line.shutter_height <= 0 or line.shutter_width <= 0:
                line.range_config_id = False
                continue

            shutter_type = line.product_template_id.shutter_type_id
            range_rule = self.env['shutter.range.config'].search([
                ('shutter_type_id', '=', shutter_type.id),
                ('min_height', '<=', line.shutter_height),
                ('max_height', '>=', line.shutter_height),
                ('min_width', '<=', line.shutter_width),
                ('max_width', '>=', line.shutter_width),
            ], limit=1)

            line.range_config_id = range_rule

            if not range_rule:
                # Warning logic is handled by Constraint on save,
                # but we can leave this here for UI feedback if needed.
                line.range_config_id = False
                continue

            if range_rule:
                valid_configs = self.env['shutter.component.config'].search([
                    ('range_config_id', '=', range_rule.id)
                ])

                line.allowed_lock_ids = valid_configs.mapped('lock_product_id')
                line.allowed_stopper_ids = valid_configs.mapped('stopper_product_id')
                line.allowed_blade_ids = valid_configs.mapped('blade_product_id')

    @api.onchange('lock_product_id', 'stopper_product_id', 'blade_product_id')
    def _onchange_components_manual(self):
        if self.blade_product_id and self.range_config_id:
            relevant_config = self.env['shutter.component.config'].search([
                ('range_config_id', '=', self.range_config_id.id),
                ('blade_product_id', '=', self.blade_product_id.id)
            ], limit=1)

            if relevant_config and relevant_config.blade_qty_formula:
                local_dict = {'height': self.shutter_height, 'width': self.shutter_width}
                try:
                    self.blade_qty = safe_eval(relevant_config.blade_qty_formula, local_dict)
                except Exception:
                    self.blade_qty = 0.0
            else:
                pass
        else:
            self.blade_qty = 0.0

        extra = 0.0
        if self.lock_product_id:
            extra += self.lock_product_id.list_price
        if self.stopper_product_id:
            extra += self.stopper_product_id.list_price
        if self.blade_product_id:
            extra += (self.blade_product_id.list_price * self.blade_qty)

        self.component_price_total = extra

        base_price = self.product_id.list_price if self.product_id else 0.0
        self.price_unit = base_price + extra


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_shutter_products = fields.Boolean(
        compute="_compute_has_shutter_products",
        store=True
    )

    @api.depends('order_line.product_template_id.is_shutter_product')
    def _compute_has_shutter_products(self):
        for order in self:
            order.has_shutter_products = any(
                line.product_template_id.is_shutter_product for line in order.order_line
            )