from odoo import api, fields, models, Command


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_promo_active = fields.Boolean(string="Active Promotion", default=False)

    promo_threshold = fields.Integer(string="Buy (Min Qty)")

    promo_reward = fields.Integer(string="Get (Free Qty)")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_free_product = fields.Boolean(string="Is Free Item",default=False)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('order_line')
    def _onchange_apply_dynamic_promo(self):
        needed_gifts = {}

        paid_totals = {}

        for line in self.order_line:
            product = line.product_id

            if not product or line.is_free_product or not product.is_promo_active:
                continue

            pid = product.id
            paid_totals[pid] = paid_totals.get(pid, 0.0) + line.product_uom_qty

        for pid, total_qty in paid_totals.items():
            product = self.env['product.product'].browse(pid)

        #     if product.promo_threshold > 0:
        #         multiplier = int(total_qty // product.promo_threshold)
        #
        #         if multiplier > 0:
        #             reward_qty = multiplier * product.promo_reward
        #             needed_gifts[pid] = reward_qty

            if product.promo_threshold > 0 and total_qty >= product.promo_threshold:
                needed_gifts[pid] = product.promo_reward

        current_gift_lines = {}

        for line in self.order_line:
            if line.is_free_product and line.product_id:
                pid = line.product_id.id
                if pid not in current_gift_lines:
                    current_gift_lines[pid] = []
                current_gift_lines[pid].append(line)

        lines_to_command = []
        all_pids = set(needed_gifts.keys()) | set(current_gift_lines.keys())

        for pid in all_pids:
            qty_needed = needed_gifts.get(pid, 0)

            existing_lines = current_gift_lines.get(pid, [])
            qty_have = sum(l.product_uom_qty for l in existing_lines)

            product = self.env['product.product'].browse(pid)

            if qty_needed > qty_have:
                to_add = int(qty_needed - qty_have)

                if to_add > 0:
                    lines_to_command.append(Command.create({
                        'product_id': pid,
                        'product_uom_qty': to_add,
                        'price_unit': 0.0,
                        'is_free_product': True,
                        'name': f"Promo: Buy {product.promo_threshold} Get {product.promo_reward} Free"
                    }))

            elif qty_have > qty_needed:
                to_remove = int(qty_have - qty_needed)

                for line in reversed(existing_lines):
                    if to_remove <= 0:
                        break

                    if line.product_uom_qty <= to_remove:
                        to_remove -= int(line.product_uom_qty)
                        lines_to_command.append(Command.delete(line.id))
                    else:
                        lines_to_command.append(Command.update(line.id, {
                            'product_uom_qty': line.product_uom_qty - to_remove
                        }))
                        to_remove = 0

        if lines_to_command:
            self.update({'order_line': lines_to_command})