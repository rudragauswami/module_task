from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    manual_base_price = fields.Float(string="Manual Base Price",digits='Product Price',default=0.0)

    visual_unit_price = fields.Float(string="Unit Price",
                                     digits='Product Price',compute='_compute_visual_price',
                                     inverse='_set_visual_price',store=True,readonly=False,)

    commission_amount = fields.Monetary(string="Commission",store=True,
                                        readonly=True,currency_field='currency_id')

    @api.depends('manual_base_price', 'component_price_total')
    def _compute_visual_price(self):
        for line in self:
            comp_val = getattr(line, 'component_price_total', 0.0)
            line.visual_unit_price = line.manual_base_price + comp_val

    def _set_visual_price(self):
        for line in self:
            comp_val = getattr(line, 'component_price_total', 0.0)
            line.manual_base_price = line.visual_unit_price - comp_val


    @api.onchange('product_id', 'shutter_height', 'shutter_width', 'visual_unit_price', 'product_uom_qty',
                  'component_price_total')
    def _recalculate_prices(self):
        for line in self:
            if line.product_id and line.manual_base_price == 0.0 and not line.component_price_total:
                line.manual_base_price = line.product_id.list_price

            base_total_for_comm = line.visual_unit_price * line.product_uom_qty
            comm_val = 0.0

            if (line.product_id and
                    hasattr(line, 'product_template_id') and
                    line.product_template_id.is_shutter_product and
                    line.shutter_height > 0 and
                    line.shutter_width > 0):

                rule = self.env['range.commission'].search([
                    ('shutter_type_id', '=', line.product_template_id.shutter_type_id.id),
                    ('min_height', '<=', line.shutter_height),
                    ('max_height', '>=', line.shutter_height),
                    ('min_width', '<=', line.shutter_width),
                    ('max_width', '>=', line.shutter_width),
                ], limit=1)

                if rule:
                    comm_val = (base_total_for_comm * rule.commission_rate) / 100.0

            line.commission_amount = comm_val

            comm_per_unit = 0.0
            if line.product_uom_qty > 0:
                comm_per_unit = comm_val / line.product_uom_qty
            line.price_unit = line.visual_unit_price + comm_per_unit