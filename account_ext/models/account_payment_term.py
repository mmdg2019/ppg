# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"
    _description = "Payment Terms"

    due_factor = fields.Integer('Due Computation Factor')

    
    _sql_constraints = [
        ('check_due_factor', 'CHECK(due_factor>=0)', 'Due computation factor must be strictly positive.')
    ]