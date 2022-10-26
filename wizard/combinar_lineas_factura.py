# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InvoiceAdvanceCombinarLineasFactura(models.TransientModel):
    _name = 'invoice.advance.combinar.lineas.facturas'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )
    producto_combinado_id = fields.Many2one("product.product", string="Producto combinado", required=False, help="Producto donde se combinarán el resto de las líneas")

    def combinar_lineas_factura(self):
        """ Combina todas las líneas actuales de una factura en una sola
        línea, manteniendo las relaciones con sus órdenes de venta """

        invoice_id = self.env['account.move'].browse(self._context.get('active_id', False))

        sale_line_ids = set()
        monto_total = 0

        self = self.with_context({'default_move_type': self._context.get('default_move_type'), 'journal_id': invoice_id.journal_id.id, 'default_partner_id': invoice_id.commercial_partner_id.id, 'default_currency_id': self.company_id.currency_id.id})

        for linea in invoice_id.invoice_line_ids:
            for sol in linea.sale_line_ids:
                if sol.product_id and sol.display_type not in ('line_section', 'line_note'):
                    sale_line_ids.add(sol.id)
            monto_total = monto_total + linea.price_unit

        nueva_linea = invoice_id.invoice_line_ids.create([])

        # Ahora si eliminamos todas las líneas actuales y agregamos la nueva línea combinada
        invoice_id.write({'invoice_line_ids': [(5,)]})
        invoice_id.write({'invoice_line_ids': [(4, nueva_linea.id)]})

        #asignamos el producto y los otros datos a la línea
        datos_actualizar = {
            'product_id': self.producto_combinado_id.id,
            'price_unit': monto_total,
            'sale_line_ids': list(sale_line_ids),
            'tax_ids': self.producto_combinado_id.taxes_id,
        }
        invoice_id.write({'invoice_line_ids': [(1, nueva_linea.id, datos_actualizar)]})
