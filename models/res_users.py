from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    access_all_reports = fields.Boolean(
        string="Access All Reports",
        compute="_compute_access_all_reports",
        inverse="_inverse_access_all_reports",
        store=False
    )

    def _compute_access_all_reports(self):
        for user in self:
            user.access_all_reports = user.has_group('all_reports.group_all_reports_user')

    def _inverse_access_all_reports(self):
        group = self.env.ref('all_reports.group_all_reports_user')
        for user in self:
            if user.access_all_reports:
                user.sudo().write({'group_ids': [(4, group.id)]})
            else:
                user.sudo().write({'group_ids': [(3, group.id)]})
