from odoo import api, fields, models

class library_book(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string="Book title",required=True)
    author_id = fields.Many2one('res.partner',string="Book Author",required=True)
    isbn = fields.Char(string="ISBN number")
    category_id = fields.Many2one('library.category',string="Book Category")
    state = fields.Selection([('available','Available'),
                              ('borrowed','Borrowed'),
                              ('lost','Lost')],string="Book State")
    borrow_count = fields.Integer(compute="compute_total_count",
                                  string="Borrow Count",
                                  store=True)

  # The custom compute logic for the book borrow count
    @api.depends('author_id','category_id','state','name')
    def compute_total_count(self):
        for book in self:
            continue
