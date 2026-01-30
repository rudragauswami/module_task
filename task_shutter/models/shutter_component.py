from odoo import fields, models

class ShutterComponentConfig(models.Model):
    _name = 'shutter.component.config'
    _description = 'Component Product Mapping'
    _rec_name = 'range_config_id'

    range_config_id = fields.Many2one('shutter.range.config', string="Range Config", required=True)
    lock_product_id = fields.Many2one('product.product', string="Lock Product")
    stopper_product_id = fields.Many2one('product.product', string="Stopper Product")
    blade_product_id = fields.Many2one('product.product', string="Blade Product")
    blade_qty_formula = fields.Char(string="Blade Qty Formula", help="Use 'height' and 'width' variables. E.g: (height / 20) + 2")