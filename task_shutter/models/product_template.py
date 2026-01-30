from odoo import fields, models


class product_template(models.Model):
    _inherit = "product.template"

    is_shutter_product = fields.Boolean("Shutter Product")
    shutter_type_id = fields.Many2one('shutter.type',string="Shutter Type")
