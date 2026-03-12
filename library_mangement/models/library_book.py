from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'


    name = fields.Char(string="Book Title", required=True)
    author_id = fields.Many2one('res.partner', string="Book Author", required=True)
    isbn = fields.Char(string="ISBN Number")
    category_id = fields.Many2one('library.category', string="Book Category")

    state = fields.Selection([('available', 'Available'),
                              ('borrowed', 'Borrowed'),
                              ('lost', 'Lost')
                              ], string="Book State", default='available', tracking=True)

    # Required for the compute function to count the tickets
    borrow_ids = fields.One2many('library.borrow', 'book_id', string="Borrow History")

    borrow_count = fields.Integer(
        compute="_compute_total_count",
        string="Borrow Count",
        store=True
    )

    @api.depends('borrow_ids')
    def _compute_total_count(self):
        for book in self:
            book.borrow_count = len(book.borrow_ids)

    def action_borrow(self):
        for book in self:
            if book.state != 'available':
                raise ValidationError("The Book is not available!")

            partner_id = self.env.user.partner_id.id
            member = self.env['library.member'].search([('partner_id', '=', partner_id)], limit=1)

            if not member:
                member = self.env['library.member'].create({'partner_id': partner_id})

            # Grab the days from the category, or default to 15 if no category is set
            days_allowed = book.category_id.max_borrow_days if book.category_id else 15

            today = fields.Date.context_today(self)
            due_date = today + timedelta(days=days_allowed)

            self.env['library.borrow'].create({
                'book_id': book.id,
                'member_id': member.id,
                'return_pre': due_date,
            })

            book.state = 'borrowed'


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Library Category'

    name = fields.Char(string="Category Name", required=True)
    book_ids = fields.One2many('library.book', 'category_id', string="Books")
    max_borrow_days = fields.Integer(string="Maximum Borrow Days", default=15, required=True)