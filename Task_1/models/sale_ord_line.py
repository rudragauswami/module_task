from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class Sale(models.Model):
    _inherit = 'sale.order.line'

    shutter_height = fields.Float('Shutter Height')
    shutter_length = fields.Float('Shutter Length')

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