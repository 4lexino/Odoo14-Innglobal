# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos sobreescritos del modelo padre
    phone = fields.Char(required=True)
    email = fields.Char(required=True)

    # Campos añadidos
    agencia = fields.Many2one(string='Agencia', comodel_name='res.partner', required=False)
    instagram = fields.Char(string="@ Instagram", required=True, store=True)