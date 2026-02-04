from odoo import fields,models,api

class ShutterRangeConfig(models.Model):
    _name = 'shutter.range.config'
    _description = 'Shutter Range Configuration'
    _rec_name = 'name'

    name = fields.Char(string="Range Label", compute="_compute_name", store=True)
    shutter_type_id = fields.Many2many('shutter.type','range_id', string="Shutter Type", required=True)
    min_height = fields.Float("Min Height", required=True)
    max_height = fields.Float("Max Height", required=True)
    min_width = fields.Float("Min Width", required=True)
    max_width = fields.Float("Max Width", required=True)

    @api.depends('shutter_type_id','min_height','max_height','min_width','max_width')

    def _compute_name(self):
        for rec in self:
            if rec.shutter_type_id:
                rec.name = f" [{rec.min_height}-{rec.max_height}-{rec.min_width}-{rec.max_width}]"

            else:
                rec.name = f"{rec.name}"
