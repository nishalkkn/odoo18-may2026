# -*- coding: utf-8 -*-
import os
from odoo import models, fields, api, tools


class ReportingWizard(models.TransientModel):
    _name = "odoo.health.report.wizard"
    _description = "Reporting Wizard"

    website = fields.Boolean("Website")
    server = fields.Boolean("Server")
    module_quality = fields.Boolean("Module Quality")
    selected_module = fields.Many2many(
        'ir.module.module',
        string="Installed Modules",
        domain=[('state', '=', 'installed')]
    )

    def action_print_odoo_health_report(self):
        """Action to print the Odoo Health report"""

        module = self.env['ir.module.module'].search([('state', '=', 'installed')])
        installed_module_name = module.mapped('name')

        addons_paths = tools.config['addons_path'].split(',')
        skipped_modules = []
        valid_modules = []

        for module_name in installed_module_name:
            module_path = next(
                (os.path.join(path, module_name) for path in addons_paths if
                 os.path.isdir(os.path.join(path, module_name))),
                None
            )

            if module_path:
                path_parts = module_path.split(os.sep)

                if any(part == 'addons' for part in path_parts):
                    skipped_modules.append((module_name))
                else:
                    valid_modules.append((module_name))  # Append the valid module and its path

        # Get the selected modules' names
        module_names = self.selected_module.mapped('name')

        data = {
            'website': self.website,
            'server': self.server,
            'module_quality': self.module_quality,
            'module_names': module_names,
            'selected_module': valid_modules# Correct key for module names
        }

        context = dict(self.env.context)
        context.update({'selected_modules': module_names})  # Add to context if needed

        return self.env.ref('odoo_health_report_tool.action_odoo_health_report').report_action(
            None,
            data=data,
            config=False,
        )

    @api.model
    def default_get(self, fields_list):
        res = super(ReportingWizard, self).default_get(fields_list)

        if self.env.context.get('selected_module'):
            res['selected_module'] = self.env.context['selected_module']

        return res
