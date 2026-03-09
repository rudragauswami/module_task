from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string="Book Title", required=True)
    author_id = fields.Many2one('res.partner', string="Book Author", required=True)
    isbn = fields.Char(string="ISBN Number")

    category_id = fields.Many2one('library.category', string="Book Category")

    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')
    ], string="Book State", default='available', tracking=True)

    borrow_ids = fields.One2many('library.borrow', 'book_id', string="Borrow History")

    borrow_count = fields.Integer(
        compute="_compute_total_count",
        string="Borrow Count",
        store=True
    )

    @api.depends('borrow_ids')
    def _compute_total_count(self):
        for book in self:
            # Simply count how many borrow records are attached to this book
            book.borrow_count = len(book.borrow_ids)

    def action_borrow(self):
        for book in self:
            if book.state == 'borrowed':
                raise ValidationError("The Book is already borrowed!")
            book.state = 'borrowed'


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Library Category'

    name = fields.Char(string="Category Name", required=True)
    book_ids = fields.One2many('library.book', 'category_id', string="Books")



