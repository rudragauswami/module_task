from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderApprovalLine(models.Model):
    _name = 'purchase.order.approval.line'
    _description = 'PO Approval Hierarchy'
    _order = 'sequence asc'

    order_id = fields.Many2one('purchase.order', string="Purchase Order", ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Approver", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved')
    ], default='pending', string="Status")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_line_ids = fields.One2many('purchase.order.approval.line', 'order_id',
                                        string="Approvers")
    is_current_approver = fields.Boolean(compute='_compute_is_current_approver')
    is_approval_pending = fields.Boolean(compute='_compute_is_approval_pending')
    pending_approver_ids = fields.Many2many('res.users',compute='_compute_pending_approvers',
                                            string="Pending Approvers")

    @api.depends('approval_line_ids', 'approval_line_ids.state', 'approval_line_ids.user_id')
    def _compute_pending_approvers(self):
        for order in self:
            pending_lines = order.approval_line_ids.filtered_domain([('state', '=', 'pending')])
            order.pending_approver_ids = pending_lines.mapped('user_id')

    @api.depends('approval_line_ids', 'approval_line_ids.state')
    def _compute_is_approval_pending(self):
        for order in self:
            pending = order.approval_line_ids.filtered_domain([('state', '=', 'pending')])
            order.is_approval_pending = bool(pending)

    @api.depends('approval_line_ids', 'approval_line_ids.state', 'approval_line_ids.user_id')
    def _compute_is_current_approver(self):
        for order in self:
            order.is_current_approver = False
            pending_lines = order.approval_line_ids.filtered_domain([('state', '=', 'pending')])
            if pending_lines and pending_lines[0].user_id == self.env.user:
                order.is_current_approver = True

    def write(self, vals):
        if 'approval_line_ids' in vals:
            for order in self:
                if order.state not in ['draft', 'sent']:
                    raise UserError("Sneaky! You cannot modify the approval hierarchy after the process has started.")

        if 'order_line' in vals:
            for order in self:
                if order.state == 'to approve':
                    raise UserError(
                        "Loophole closed! You cannot change products or quantities while the order is waiting for approvals. Please cancel and reset to draft to make changes.")

        for order in self:
            if order.state in ['draft', 'sent', 'to approve']:
                if order.create_uid and order.create_uid != self.env.user and not self.env.su:
                    raise UserError("Only the user who created this Purchase Order is allowed to edit it.")

        return super().write(vals)

    def button_draft(self):
        res = super().button_draft()
        for order in self:
            order.approval_line_ids.write({'state': 'pending'})
        return res


    def button_confirm(self):
        for order in self:
            if order.is_approval_pending:
                raise UserError(
                    "Access Denied: You cannot confirm this order until all assigned approvers have completed their step-by-step approval.")
        return super().button_confirm()

    def action_step_approve(self):
        self.ensure_one()
        pending_lines = self.approval_line_ids.filtered_domain([('state', '=', 'pending')])

        if not pending_lines:
            raise UserError("There are no pending approvals.")

        current_approver = pending_lines[0]

        if current_approver.user_id != self.env.user:
            raise UserError("It is not your turn to approve this order yet.")

        current_approver.sudo().write({'state': 'approved'})

        if len(pending_lines) == 1:
            self.sudo().button_confirm()
        else:
            if self.state in ['draft', 'sent']:
                self.sudo().write({'state': 'to approve'})