from odoo import fields, models


class product_template(models.Model):
    _inherit = "product.template"

    is_apron_shutter = fields.Boolean('Appron Shutter')
    min_height = fields.Float('Minimum Height (in meters)')
    max_height = fields.Float('Maximum Height (in meters)')
    min_length = fields.Float('Minimum Length (in meters)')
    max_length = fields.Float('Maximum Length (in meters)')
