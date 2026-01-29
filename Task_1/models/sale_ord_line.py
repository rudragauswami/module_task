from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class Sale(models.Model):
    _inherit = 'sale.order.line'

    shutter_height = fields.Float('Shutter Height')
    shutter_length = fields.Float('Shutter Length')
    compute_shutter_area = fields.Float(compute='_compute_compute_shutter_area', string='Shutter Area', store=True)
    is_apron_shutter = fields.Boolean(string='Appron Shutter',
                               related='product_template_id.is_apron_shutter',
                               readonly = True, store = True)


    @api.constrains('shutter_height', 'shutter_length', 'product_id')
    def _check_apron_shutter_dimensions(self):
        for line in self:
            product = line.product_id.product_tmpl_id

            if product.is_apron_shutter:
                if not (product.min_height <= line.shutter_height <= product.max_height):
                    raise ValidationError(
                        '''Selected Apron Shutter product has dimension limits.
                           Please reset Height or Length within allowed range.'''
                    )

                if not (product.min_length <= line.shutter_length <= product.max_length):
                    raise ValidationError(
                        ''' Selected Apron Shutter product has dimension limits.
                            Please reset Height or Length within allowed range.'''
                    )

    @api.depends('shutter_height', 'shutter_length')
    def _compute_compute_shutter_area(self):
        for line in self:
            line.compute_shutter_area = line.shutter_height * line.shutter_length

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_shutter_type = fields.Selection([('manual', 'Manual'), ('auto', 'Automatic')], string="Shutter Type")

    has_apron_lines = fields.Boolean(compute="_compute_has_apron_lines", store=True)

    @api.depends('order_line.is_apron_shutter')
    def _compute_has_apron_lines(self):
        for order in self:
            order.has_apron_lines = any(line.is_apron_shutter for line in order.order_line)

