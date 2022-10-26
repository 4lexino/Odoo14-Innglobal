# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contacto_pago = fields.Char(string="Contacto de pago", store=True)
