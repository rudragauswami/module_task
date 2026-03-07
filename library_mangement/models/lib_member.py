from odoo import api, fields, models

class lib_member(models.Model):
    _name = 'library.member'
    _description = 'Library Member'


    partner_id = fields.Many2one('res.partner',required=True,string='Linked contact')
    membership_date = fields.Datetime(string='Date of Registration')
    borrow_ids = fields.One2many('library.borrow','member_id',string='Borrow History')
    active = fields.Boolean(default=True,string='Is Active Member')