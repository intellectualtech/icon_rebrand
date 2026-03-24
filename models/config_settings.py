import base64
import os
from odoo import models, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_icon_mapping(self):
        """ module_name → your actual icon filename (without .png) """
        return {
            'sale_management': 'sales',
            'crm': 'crm',
            'stock': 'inventory',
            'account': 'accounting',
            'purchase': 'purchase',
            'point_of_sale': 'point_of_sale',
            'pos_restaurant': 'kitchen_display',        # or 'point_of_sale'
            'project': 'projects',                      # you have "projects .png" and "projects (1).png"
            'mrp': 'manufacturing',
            'hr': 'employee',
            'hr_expense': 'expenses',
            'website': 'website',
            'documents': 'documents',
            'web_studio': 'apps',                       # or 'dashboard'
            'mass_mailing': 'email_marketing',
            'equity': 'accounting',                     # fallback
            'timesheet_grid': 'timesheets',
            'appointment': 'appointment',
            'recruitment': 'recruitment',
            'maintenance': 'maintenance',
            'field_service': 'field_service',
        }

    def action_apply_custom_app_icons(self):
        self.ensure_one()
        mapping = self._get_icon_mapping()
        module_name = 'rebrand_icons'
        updated_count = 0

        for mod_name, file_base in mapping.items():
            icon_path = get_module_resource(module_name, 'static/icons', f"{file_base}.png")
            if not icon_path or not os.path.exists(icon_path):
                continue

            with open(icon_path, 'rb') as f:
                icon_data = base64.b64encode(f.read())

            menus = self.env['ir.ui.menu'].search([
                ('parent_id', '=', False),
                ('module', '=', mod_name),
            ])

            if not menus:
                menus = self.env['ir.ui.menu'].search([
                    ('parent_id', '=', False),
                    ('name', 'ilike', mod_name.replace('_', ' ').title()),
                ])

            if menus:
                menus.write({
                    'web_icon_data': icon_data,
                    'web_icon': False,
                })
                updated_count += len(menus)

        if updated_count == 0:
            raise UserError(_("No icons applied.\nMake sure your PNG files exist in static/icons/"))

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }