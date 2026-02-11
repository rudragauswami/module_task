from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commission_amount = fields.Float(
        string="Commission",
        compute="_compute_commission",
        store=True
    )

    @api.depends('product_id', 'shutter_height', 'shutter_width', 'component_price_total', 'product_uom_qty')
    def _compute_commission(self):
        for line in self:
            commission = 0.0
            base_price = line.product_id.list_price if line.product_id else 0.0
            component_price = line.component_price_total or 0.0

            subtotal_before_commission = (base_price + component_price) * line.product_uom_qty

            if (line.product_id and
                    hasattr(line, 'product_template_id') and
                    line.product_template_id.is_shutter_product and
                    line.shutter_height > 0 and
                    line.shutter_width > 0):

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

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids', 'commission_amount','component_price_total')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            if line.commission_amount:
                line.price_subtotal+=line.commission_amount

                line.price_total+=line.commission_amount


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_tax_totals_summary(self, base_lines, currency, company, cash_rounding=None):
        """
        Override to inject 'commission_amount' into the tax widget totals.
        Since commission is added directly to subtotal , we must add it
        to the 'Untaxed Amount' and 'Total' in the summary.
        """

        summary = super()._get_tax_totals_summary(base_lines, currency, company, cash_rounding)

        total_commission_currency = 0.0
        total_commission_base = 0.0

        for line in base_lines:
            record = line.get('record')


            if record and record._name == 'sale.order.line' and getattr(record, 'commission_amount', 0.0):
                amount = record.commission_amount

                total_commission_currency += amount

                rate = line.get('rate', 1.0)
                if rate:
                    total_commission_base += amount / rate

        if total_commission_currency != 0.0:

            summary['base_amount_currency'] += total_commission_currency
            summary['base_amount'] += total_commission_base

            summary['total_amount_currency'] += total_commission_currency
            summary['total_amount'] += total_commission_base

            for subtotal in summary.get('subtotals', []):
                if subtotal.get('name') == 'Untaxed Amount':
                    subtotal['base_amount_currency'] += total_commission_currency
                    subtotal['base_amount'] += total_commission_base

        return summary