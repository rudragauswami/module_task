from odoo import fields,models,api

class libraryBorrow(models.Model):
    _name = 'library.borrow'
    _description = 'Library Borrow'

    book_id = fields.Many2one('library.book',string='Book',required=True)
    member_id = fields.Many2one('library.member',string='Member',required=True)
    borrow_date = fields.Datetime(string='Borrow Date',default=fields.Date.today())
    return_date = fields.Datetime(string='Return Date')
    state = fields.Selection([('borrowed','Borrowed'),('returned','Returned'),
                              ('overdue','Overdue')],string='State')