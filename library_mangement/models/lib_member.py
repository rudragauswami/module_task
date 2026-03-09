from odoo import api, fields, models


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', required=True, string='Linked Contact')
    membership_date = fields.Datetime(string='Date of Registration', default=fields.Datetime.now)
    borrow_ids = fields.One2many('library.borrow', 'member_id', string='Borrow History')
    active = fields.Boolean(default=True, string='Is Active Member')