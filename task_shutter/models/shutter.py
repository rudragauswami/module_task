from odoo import fields, models, api


class ShutterType(models.Model):
    _name = 'shutter.type'


    name = fields.Char("Shutter Name",required=True)
    code = fields.Char("Shutter Code",required=True)
    active = fields.Boolean("Is Active",default=True)
    range_id = fields.Many2many(
        'shutter.range.config','shutter_type_id',string='range rules' )


