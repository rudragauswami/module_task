from odoo import fields, models, api
from odoo.exceptions import ValidationError


class LibraryBorrow(models.Model):
    _name = 'library.borrow'
    _description = 'Library Borrow'
    _rec_name = 'member_id'


    book_id = fields.Many2one('library.book', string='Book', required=True)
    member_id = fields.Many2one('library.member', string='Member', required=True)
    borrow_date = fields.Date(string='Borrow Date', default=fields.Date.context_today)
    return_date = fields.Date(string='Return Date')
    state = fields.Selection([('borrowed', 'Borrowed'),('returned', 'Returned'),
                              ('overdue', 'Overdue')], string='State', default='borrowed')

    def action_return(self):
        for record in self:
            record.state = 'returned'

    @api.constrains('book_id', 'state')
    def _check_book_available(self):
        for record in self:
            if record.state == 'borrowed' and record.book_id.state == 'borrowed':
                other_active_borrows = self.env['library.borrow'].search([
                    ('book_id', '=', record.book_id.id),
                    ('state', '=', 'borrowed'),
                    ('id', '!=', record.id)
                ])
                if other_active_borrows:
                    raise ValidationError(f"'{record.book_id.name}' is currently borrowed by someone else!")