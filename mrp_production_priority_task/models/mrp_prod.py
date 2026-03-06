from odoo import fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    priority = fields.Selection(selection_add=[('2', 'Medium Priority'),
                                               ('3', 'High Priority')],)


class StockMove(models.Model):
    _inherit = 'stock.move'

    priority = fields.Selection(selection_add=[('2', 'Medium Priority'),
                                               ('3', 'High Priority')], )
