from odoo import fields,models,api

class ShutterRangeConfig(models.Model):
    _name = 'shutter.range.config'
    _description = 'Shutter Range Configuration'
    _rec_name = 'shutter_type_id'

    shutter_type_id = fields.Many2one('shutter.type', string="Shutter Type", required=True)
    min_height = fields.Float("Min Height", required=True)
    max_height = fields.Float("Max Height", required=True)
    min_width = fields.Float("Min Width", required=True)
    max_width = fields.Float("Max Width", required=True)