# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # CAMPOS HEREDADOS

    # CAMPOS NUEVOS

    count_line_ids_combinables = fields.Integer(string="Conteo de líneas de factura aptas para ser combinadas", store=False, compute="_get_count_combinables_lines", default=0)
    tipo_comprobante_from_venta = fields.Selection([
        ('recibo','Recibo'),
        ('factura','Factura'),
    ], string='Tipo de comprobante (Por cotización)', store=True, readonly=True)



    # MÉTODOS HEREDADOS

    # MÉTODOS NUEVOS

    @api.depends('invoice_line_ids')
    def _get_count_combinables_lines(self):
        conteo = 0
        for factura in self:
            for line in factura.invoice_line_ids:
                if line.product_id and line.display_type not in ('line_section', 'line_note'):
                    conteo = conteo + 1

        self.count_line_ids_combinables = conteo

    @api.model
    def _ligar_factura_con_lineas_de_orden_venta(self):
        """ Esta función detecta mediante el campo 'invoice_origin' de dónde
         se originó la factura para volverla a ligar con sus líneas de la
         orden de venta. """

        # Nos aseguramos solo aceptar 1 registro
        self.ensure_one()

        # Nos aseguramos que en la factura hay una sola línea (sin contar secciones o notas)
        if self.count_line_ids_combinables != 1:
            raise UserError("Solo se puede ligar a facturas con 1 línea")

        # Nos aseguramos que esa única línea no venga de una orden de venta ya
        if len(self.invoice_line_ids[0].sale_line_ids) > 0:
            raise UserError("Solo se puede ligar a facturas que no estén ligadas ya a una órden de venta")

        # Primero obtenemos el órigen de la factura
        str_ordenes_origen = self.invoice_origin.split(', ')

        # Obtenemos los ids de las órdenes órigen
        ordenes_origen_ids = self.env['sale.order'].search([('name', 'in', str_ordenes_origen)])

        suma_total_ordenes = 0
        order_lines_ids = set()

        for orden in ordenes_origen_ids:
            suma_total_ordenes = suma_total_ordenes + orden.amount_total

            for linea in orden.order_line:
                order_lines_ids.add(linea.id)

        if suma_total_ordenes != self.amount_total:
            raise UserError(
                "El monto total de la factura no coincide con el monto total de las órdenes de venta origen.")

        self.invoice_line_ids[0].write({'sale_line_ids': [(6, 0, order_lines_ids)]})

    @api.model
    def _ligar_factura_con_lineas_de_orden_venta_forzado(self):
        # Nos aseguramos solo aceptar 1 registro
        self.ensure_one()

        # Nos aseguramos que en la factura hay una sola línea (sin contar secciones o notas)
        if self.count_line_ids_combinables != 1:
            raise UserError("Solo se puede ligar a facturas con 1 línea")

        # Nos aseguramos que esa única línea no venga de una orden de venta ya
        if len(self.invoice_line_ids[0].sale_line_ids) > 0:
            raise UserError("Solo se puede ligar a facturas que no estén ligadas ya a una órden de venta")

        # Primero obtenemos el órigen de la factura
        str_ordenes_origen = self.invoice_origin.split(', ')

        # Obtenemos los ids de las órdenes órigen
        ordenes_origen_ids = self.env['sale.order'].search([('name', 'in', str_ordenes_origen)])

        suma_total_ordenes = 0
        order_lines_ids = set()

        for orden in ordenes_origen_ids:
            suma_total_ordenes = suma_total_ordenes + orden.amount_total

            for linea in orden.order_line:
                order_lines_ids.add(linea.id)

        # if suma_total_ordenes != self.amount_total:
        #     raise UserError(
        #         "El monto total de la factura no coincide con el monto total de las órdenes de venta origen.")

        self.invoice_line_ids[0].write({'sale_line_ids': [(6, 0, order_lines_ids)]})


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # CAMPOS HEREDADOS

    # CAMPOS NUEVOS

    # MÉTODOS HEREDADOS

    # def unlink(self):
    #     for item in self:
    #         if len(item.sale_line_ids) > 0:
    #             raise ValidationError("No se pueden eliminar líneas relacionadas a una orden de venta.")
    #     return super(AccountMoveLine, self).unlink()

    # MÉTODOS NUEVOS

    # def delete_linea(self):
    #     """ Función previa a desvincular el record con la factura
    #     Primero, advertimos al usuario que está intentando desvincular una
    #     línea relacionada a una órden de venta"""
    #
    #     self.ensure_one()
    #
    #     if len(self.sale_line_ids) > 0:
    #         return {'value':{},'warning':{'title':'warning','message':'Your message'}}
    #
    #     self.unlink()