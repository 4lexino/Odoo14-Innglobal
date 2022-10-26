# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        tipo_comprobante_temp = set()

        for orden in sale_orders:
            tipo_comprobante_temp.add(orden.tipo_comprobante)

        if len(tipo_comprobante_temp) > 1:
            raise ValidationError("Las órdenes seleccionadas contienen distintos tipos en el campo 'Tipo de comprobante (recibo o factura)'")

        return super(SaleAdvancePaymentInv, self).create_invoices()