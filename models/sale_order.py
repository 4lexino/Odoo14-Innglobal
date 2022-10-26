# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # CAMPOS HEREDADOS

    invoice_status = fields.Selection(selection_add=[('pagado', 'Pagado')])
    origin = fields.Char(store=True, compute="_actualiza_documento_origen")
    date_order = fields.Datetime(readonly=False)
    tag_ids = fields.Many2many(readonly=False, compute="_actualiza_tags_lead")

    # CAMPOS NUEVOS

    fecha_lim_facturacion = fields.Date(string='Fecha límite de facturación', required=False, track_visibility='onchange')
    talento = fields.Char(string="Talento", store=True, compute="_get_talento")
    agencia = fields.Char(string="Agencia", store=True, compute="_get_agencia")
    etapa_lead = fields.Char(string="Etapa CRM", store=True, compute="_get_etapa_lead")
    tipo_comprobante = fields.Selection([
        ('recibo','Recibo'),
        ('factura','Factura'),
    ], string='Tipo de comprobante', default='factura', required=True, tracking=True)



    # MÉTODOS HEREDADOS

    def _prepare_invoice(self):
        """ Extendemos la funcionalidad para incluir el campo 'tipo_comprobante'
         en la factura. """
        self.ensure_one()

        datos_factura = super(SaleOrder, self)._prepare_invoice()

        datos_factura.update({'tipo_comprobante_from_venta': self.tipo_comprobante})

        return datos_factura;

    # MÉTODOS NUEVOS

    @api.depends('opportunity_id.tag_ids')
    def _actualiza_tags_lead(self):
        for orden in self:
            if orden.opportunity_id:
                orden.write({'tag_ids': [(5,)]})
                for tag in orden.opportunity_id.tag_ids:
                    orden.write({'tag_ids': [(4, tag.id)]})

    def _calcular_importe_pendiente_total(self, order):
        importe_pendiente = -1

        if len(order.invoice_ids) == 1:
            importe_pendiente = order.invoice_ids.amount_residual
        elif len(order.invoice_ids) > 1:
            importe_pendiente = 0
            for factura in order.invoice_ids:
                importe_pendiente = importe_pendiente + factura.amount_residual

        return importe_pendiente

    @api.depends('opportunity_id')
    def _actualiza_documento_origen(self):
        for orden in self:
            if orden.opportunity_id:
                orden['origin'] = orden.opportunity_id.name

    @api.depends('opportunity_id')
    def _get_etapa_lead(self):
        for orden in self:
            if orden.opportunity_id:
                orden['etapa_lead'] = orden.opportunity_id.stage_id.name

    @api.depends('opportunity_id')
    def _get_talento(self):
        for orden in self:
            if orden.opportunity_id.talento_id:
                orden['talento'] = orden.opportunity_id.talento_id.name
            else:
                orden['talento'] = ''

    @api.depends('partner_id')
    def _get_agencia(self):
        for orden in self:
            if orden.partner_id.agencia:
                orden['agencia'] = orden.partner_id.agencia.name
            else:
                orden['agencia'] = ''


    def _formatLang(self, value):
        lang = self.partner_id.lang
        lang_objs = self.env['res.lang'].search([('code', '=', lang)])
        if not lang_objs:
            lang_objs = self.env['res.lang'].search([], limit=1)
        lang_obj = lang_objs[0]

        res = lang_obj.format('%.' + str(2) + 'f', value, grouping=True, monetary=True)
        currency_obj = self.currency_id

        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = '%s %s' % (res, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = '%s %s' % (currency_obj.symbol, res)
        return res

    def _obtenerInfluencerVariante(self, producto):
        for va in producto.variant_seller_ids:
            if va.product_id.id == producto.id:
                return va.name

    def _groupByAccion(self, lineas):
        accion_influencers = {}

        for linea in lineas:
            if not linea.display_type:
                influencer = self._obtenerInfluencerVariante(linea.product_id)

                if not linea.product_template_id.name in accion_influencers:
                    accion_influencers[linea.product_template_id.name] = [influencer.name]
                else:
                    accion_influencers[linea.product_template_id.name] = accion_influencers[linea.product_template_id.name] + [influencer.name]

        return accion_influencers

    def _tablaInfluencersAcciones(self, lineas):
        influencer_acciones = {}
        influencers = []
        acciones = []

        ## Obtenemos la lista de influencers únicos y acciones únicas
        for linea in lineas:
            if not linea.display_type:
                influencer = self._obtenerInfluencerVariante(linea.product_id)

                if not influencer.name in influencers:
                    influencers.append(influencer.name)

                if not linea.product_template_id.name in acciones:
                    acciones.append(linea.product_template_id.name)

        for influencer in influencers:
            valor = []
            for accion in acciones:
                valor_aux = "N/A"
                for linea in lineas:
                    influencer_aux = self._obtenerInfluencerVariante(linea.product_id)

                    if influencer_aux.name == influencer and linea.product_template_id.name == accion:
                        valor_aux = linea.price_unit
                        break
                valor = valor + [valor_aux]
            influencer_acciones[influencer] = valor

        respuesta = {
            "tabla_influencer_precios": influencer_acciones,
            "lista_acciones": acciones
        }

        return respuesta

    def action_enviar_order_venta(self, template_id):
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "innglobal.mail_notification_innglobal",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
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

    def action_enviar_cotizacion(self):
        self.ensure_one()
        template_id = int(self.env['ir.config_parameter'].sudo().get_param('innglobal.default_envio_cotizacion'))

        return self.action_enviar_order_venta(template_id)

    def action_enviar_confirmacion_contado(self):
        self.ensure_one()
        template_id = int(self.env['ir.config_parameter'].sudo().get_param('innglobal.default_confirmacion_cotizacion_contado'))

        return self.action_enviar_order_venta(template_id)

    def action_enviar_confirmacion_grande(self):
        self.ensure_one()
        template_id = int(self.env['ir.config_parameter'].sudo().get_param('innglobal.default_confirmacion_cotizacion_grande'))

        return self.action_enviar_order_venta(template_id)

    def _verificar_pago(self):
        for orden in self:
            importe_pendiente = orden._calcular_importe_pendiente_total(orden)

            if importe_pendiente == 0:
                orden.invoice_status = 'pagado'

    #ACCIONES PLANIFICADAS

    @api.model
    def _verificar_pagos_todo(self):
        ordenes = self.search([])

        for orden in ordenes:
            importe_pendiente = orden._calcular_importe_pendiente_total(orden)

            if importe_pendiente == 0:
                orden.invoice_status = 'pagado'
