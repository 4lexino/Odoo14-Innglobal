# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        #OVERWIRTE
        res = super().write(vals)

        if 'stage_id' in vals:
            if self.sale_order_id:
                # Antes de actualizar verificamos que si la venta es al contado y tiene pago pendiente
                nombre_terminos_pago = self.sale_order_id.payment_term_id.name  # obtenemos los terminos de pago de la orden relacionada

                if nombre_terminos_pago == 'Contado':
                    self.sale_order_id._verificar_pago()
                    estado_factura = self.sale_order_id.invoice_status

                    if estado_factura != 'pagado':
                        raise UserError("Pago pendiente")

        return res