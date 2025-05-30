# -*- coding: utf-8 -*-
from odoo import models, api


class OdooHealthReport(models.AbstractModel):
    _name = "report.odoo_health_report_tool.odoo_health_report"
    _description = "Odoo Health Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        website_dict = {}
        server_dict = {}
        module_quality_dict = {}

        if data.get('website'):
            seo = self.env['website.seo.details']
            performance = self.env['website.performance.details']
            security = self.env['website.security.details']
            ui = self.env['website.ui.details']
            website_dict['performance_details'] = performance.performance_details
            website_dict['seo_details'] = seo.seo_details
            website_dict['security_headers'] = security.check_security_headers
            website_dict['csp'] = security.check_csp_components
            website_dict['internal_external_links'] = seo.check_internal_external_social_media_links
            website_dict['css_js_html_files'] = performance.check_minification
            website_dict['robots_txt_sitemap_xml'] = seo.check_robots_txt
            website_dict['search_option'] = ui.check_search_option
            website_dict['image_optimization'] = performance.check_image_optimization
            website_dict['seo_friendly_url'] = seo.is_url_seo_friendly
        else:
            website_dict = None

        if data.get('server'):
            database_metrics = self.env['database.metrics']
            server_metrics = self.env['system.metrics']
            server_dict['server_metrics'] = server_metrics.get_metrics_data
            server_dict['up_time'] = server_metrics.get_server_uptime
            server_dict['database_metrics'] = database_metrics.collect_metrics
            server_dict['file_health'] = database_metrics.odoo_file_health
            server_dict['connections'] = database_metrics.get_concurrent_session_count
        else:
            server_dict = None

        if data.get('module_quality'):
            module_quality = self.env['module.quality']
            module_quality_dict['field_details'] = module_quality.count_of_non_stored_fields
            module_quality_dict['naming_convention'] = module_quality.module_naming_conventions
            module_quality_dict['count_lines'] = module_quality.count_lines_of_code_in_modules

            selected_modules = data.get('module_names', [])
            all_modules = data.get('selected_module', [])
            violations = []

            if selected_modules:
                for selected_module in selected_modules:
                    violations.append(module_quality.pep_module_filter(selected_module))

                module_quality_dict['violations'] = violations
            else:
                for module in all_modules:
                    violations.append(module_quality.pep_module_filter(module))

                module_quality_dict['violations'] = violations
        else:
            module_quality_dict = None

        return {
            'doc_ids': docids,
            'doc_model': 'module.quality',
            'docs': self,
            'server': server_dict,
            'website': website_dict,
            'module_quality': module_quality_dict,
            'selected_module': data.get('module_names')  # Ensure this is the correct key
        }
