# -*- coding: utf-8 -*-
##############################################################################
#                 @author Cooperos
#
##############################################################################

{
    'name': 'innglobal',
    'version': '0.1',
    'category': 'Sales/Sales',
    'summary': 'Lógica de negocio de InnGlobal y reportes PDF.',
    'description': """
Este módulo contiene lógica de negocio y reportes para InnGlobal Agency.
    """,
    'author': "Cooperos",
    'website': "https://cooperos.com",
    'depends': [
        'base','sale','crm','sale_project','mail','contacts','account','account_payment','project','web','portal','website'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/innglobal_security.xml',
        'report/reports_sale_order.xml',
        'report/cotizacion_sin_precios_view.xml',
        'report/cotizacion_con_precios_view.xml',
        'report/cotizacion_tabla_view.xml',
        'report/cotizacion_multiple_view.xml',
        'report/reports_account_payment.xml',
        'report/recibo_de_pago_view.xml',
        'views/view_res_partner_form.xml',
        'views/view_sale_order_form.xml',
        'views/view_sale_order_tree.xml',
        'views/view_crm_tree.xml',
        'views/view_crm_form.xml',
        'views/view_account_payment_form.xml',
        'views/view_sale_order_search.xml',
        'views/view_account_move.xml',
        'views/view_account_move_tree.xml',
        'views/crm_actions.xml',
        'views/project_actions.xml',
        'wizard/combinar_lineas_factura_views.xml',
        'data/email_templates.xml',
        'data/sale_data.xml',
        'website/cotizador.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
