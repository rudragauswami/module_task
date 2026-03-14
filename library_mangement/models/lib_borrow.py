from odoo import fields, models, api
from odoo.exceptions import ValidationError

class LibraryBorrow(models.Model):
    _name = 'library.borrow'
    _description = 'Library Borrow'
    _rec_name = 'member_id'

    book_id = fields.Many2one('library.book', string='Book', required=True)
    member_id = fields.Many2one('library.member', string='Member', required=True)
    borrow_date = fields.Date(string='Borrow Date', default=fields.Date.context_today)
    return_date = fields.Date(string='Return Date',readonly=True)
    return_pre = fields.Date(string='Pre Return Date', required=True, help="when you will return book!")

    state = fields.Selection([('borrowed', 'Borrowed'),
                              ('returned', 'Returned'),
                              ('overdue', 'Overdue')
                              ], string='State', default='borrowed')

    @api.constrains('book_id')
    def _check_book_availability(self):
        for record in self:
            # Check if a book is selected, and if its state is anything other than 'available'
            if record.book_id and record.book_id.state != 'available':
                raise ValidationError("You cannot borrow a book that is currently not available!")

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super(LibraryBorrow, self).create(vals_list)
        for ticket in tickets:
            # it sets the book state to boroowed in library.book model
            if ticket.state == 'borrowed' and ticket.book_id:
                ticket.book_id.sudo().state = 'borrowed'
        return tickets

    def unlink(self):
        for ticket in self:
            # If they are deleting an old, already 'returned' book record then nothing happen!
            if ticket.state in ['borrowed', 'overdue'] and ticket.book_id:
                # Use .sudo() so a regular librarian doesn't get an Access Error!
                ticket.book_id.sudo().state = 'available'

        return super(LibraryBorrow, self).unlink()

    def action_return(self):
        for record in self:
            record.sudo().state = 'returned'
            record.sudo().return_date = fields.Date.context_today(record)
            record.book_id.sudo().state = 'available'


    def action_send_overdue_mail(self):
        self.ensure_one()

        ctx = {
            'default_model': 'library.borrow',
            'default_res_ids': self.ids,
            'default_composition_mode': 'comment',
            'default_subject': "LIBRARY NOTICE: %s" % self.book_id.name,
            'default_body': """
                <p>Dear %(name)s,</p>
                <p>This is a manual reminder regarding your borrowed book, <strong>%(book)s</strong>. 
                The expected return date is %(date)s.</p>
                <p>Please ensure it is returned to the library on time.</p>
            """ % {
                'name': self.member_id.partner_id.name,
                'book': self.book_id.name,
                'date': self.return_pre
            },
            'default_partner_ids': [self.member_id.partner_id.id],
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    @api.model
    def _cron_check_overdue_books(self):
        today = fields.Date.context_today(self)

        # Search using 'return_pre' (The Expected Due Date) instead of 'return_date'
        overdue_tickets = self.search([
            ('state', '=', 'borrowed'),
            ('return_pre', '<', today)
        ])

        for ticket in overdue_tickets:
            # Update the state to overdue
            ticket.state = 'overdue'
            partner = ticket.member_id.partner_id

            # Send the email in the background
            if partner.email:
                mail_values = {
                    'subject': "OVERDUE NOTICE: %s" % ticket.book_id.name,
                    'body_html': """
                            <p>Dear %(name)s,</p>
                            <p>This is an automated notification. Your borrowed book, 
                            %(book)s, was due on %(date)s and is now officially overdue.</p>
                            <p>Please return it immediately.</p>
                        """ % {
                        'name': partner.name,
                        'book': ticket.book_id.name,
                        'date': ticket.return_pre
                    },
                    'email_to': partner.email,
                }
                self.env['mail.mail'].create(mail_values).send()