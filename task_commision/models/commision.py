from odoo import api, fields, models

class CommissionRule(models.Model):
    _name = 'range.commission'
    _description = 'Shutter Commission Rule'

    name = fields.Char(string='Rule Name', compute='_compute_name', store=True)

    shutter_type_id = fields.Many2one('shutter.type', string="Shutter Type", required=True)

    min_height = fields.Float('Min Height', required=True, default=0.0)
    max_height = fields.Float('Max Height', required=True, default=0.0)
    min_width = fields.Float('Min Width', required=True, default=0.0)
    max_width = fields.Float('Max Width', required=True, default=0.0)

    commission_rate = fields.Float(string='Commission Rate (%)', required=True)

    @api.depends('shutter_type_id', 'min_height', 'max_height', 'min_width', 'max_width', 'commission_rate')
    def _compute_name(self):
        for rec in self:
            type_name = rec.shutter_type_id.name if rec.shutter_type_id else "Any"
            rec.name = f"{type_name} [{rec.min_height}-{rec.max_height} x {rec.min_width}-{rec.max_width}] -> {rec.commission_rate}%"