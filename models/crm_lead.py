# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class CRMLeadSaleOrder(models.Model):
    _inherit = 'crm.lead'

    # CAMPOS HEREDADOS

    # CAMPOS NUEVOS
    dias_en_etapa = fields.Integer(string="Días en la etapa", readonly=True, store=False, compute="_get_dias_etapa")
    talento_id = fields.Many2one(string="Talento", comodel_name="res.partner", store=True, required=False)
    is_stage_won = fields.Boolean(string="La etapa del lead es ganada?", compute="_is_stage_won")

    # CRUD

    def write(self, vals):
        res = super(CRMLeadSaleOrder, self).write(vals)

        if 'stage_id' in vals.keys():
            for lead in self:
                for orden in lead.order_ids:
                    orden.write({ 'etapa_lead': lead.stage_id.name })

                    if lead.stage_id.name == "Ganado" and lead.is_stage_won:
                        if orden.state in ('draft', 'sent'):
                            orden.action_confirm()


        return res

    # METHODS

    @api.depends('date_last_stage_update')
    def _get_dias_etapa(self):

        for lead in self:
            hoy = datetime.today()
            ultima_actualizacion = lead.date_last_stage_update

            lead['dias_en_etapa'] = (hoy - ultima_actualizacion).days

    def action_enviar_correo(self, template_id):
        # lang = self.env.context.get('lang')
        # template = self.env['mail.template'].browse(template_id)
        # if template.lang:
        #     lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'crm.lead',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "innglobal.mail_notification_innglobal",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).type_name,
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

    def action_enviar_encuesta(self):
        self.ensure_one()
        # template_id = int(self.env['ir.config_parameter'].sudo().get_param('innglobal.default_envio_cotizacion'))
        template_id = self.env['ir.model.data'].xmlid_to_res_id('innglobal.email_template_envio_encuesta_satisfaccion', raise_if_not_found=False)

        return self.action_enviar_correo(template_id)

    def _is_stage_won(self):
        for lead in self:
            lead['is_stage_won'] = lead.stage_id.is_won