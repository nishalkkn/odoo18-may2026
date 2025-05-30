# -*- coding: utf-8 -*-
import ast
import base64
import glob
import os
import re
import subprocess
import time
from odoo import api, models, tools


class ModuleQuality(models.Model):
    _name = 'module.quality'
    _description = "Module Quality Metrics"

    @api.model
    def modules_installed(self):
        """function to fetch installed modules"""

        installed_modules_dict = {}
        installed_modules = self.env['ir.module.module'].search([('state', '=', 'installed')])
        for module in installed_modules:
            installed_modules_dict[module.name] = module.name
        return installed_modules_dict

    @api.model
    def count_lines_of_code_in_modules(self):
        """Count lines of Python, JavaScript, and XML code in all installed Odoo modules."""

        modules_loc = {}
        addons_paths = tools.config['addons_path'].split(',')
        installed_modules = self.modules_installed()

        for module_name in installed_modules:
            module_path = next(
                (os.path.join(path, module_name) for path in addons_paths if
                 os.path.isdir(os.path.join(path, module_name))),
                None
            )

            if module_path:
                loc = {ext: 0 for ext in [".py", ".js", ".xml"]}
                for ext in loc:
                    for file in glob.glob(os.path.join(module_path, '**', f'*{ext}'), recursive=True):
                        if '__init__.py' not in file and '__manifest__.py' not in file:
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                loc[ext] += len(f.readlines())

                modules_loc[module_name] = {
                    "py_lines": loc[".py"],
                    "js_lines": loc[".js"],
                    "xml_lines": loc[".xml"],
                }
        return modules_loc

    @api.model
    def module_naming_conventions(self):
        """to check the modules follows correct naming convention"""

        naming_pattern = re.compile("^[a-z0-9_]+$")
        installed_modules = self.modules_installed()
        invalid_module = [
            module_name for module_name in installed_modules
            if not naming_pattern.match(module_name) or module_name.endswith('_') or module_name.startswith('_')
        ]
        return {'invalid_module': invalid_module}

    @api.model
    def count_of_non_stored_fields(self):
        """Get the count of fields in database"""

        total = self.env['ir.model.fields'].search([])
        non_stored = total.search_count([('store', '=', False)])
        model_stored = total.search_count([('store', '=', True)])
        return {'nonstored_fields': non_stored,
                'stored_fields': model_stored,
                'total_fields': len(total)}

    @api.model
    def module_load_time(self):
        """return overall module load time """

        start_time = time.time()
        loaded_modules = []
        processed_modules = []

        installed_modules = self.modules_installed()
        for index, module_name in enumerate(installed_modules, 1):
            time.sleep(0.1)  # Simulate processing time
            loaded_modules.append(module_name)
            processed_modules.append(module_name)

        end_time = time.time()
        total_time_taken = end_time - start_time
        print(f"Total installation time for {len(installed_modules)} modules: {total_time_taken:.2f} seconds")
        return total_time_taken

    @api.model
    def pep_module_filter(self, selected_module):
        """ checks pep8 standards of installed modules"""

        violations_list = []

        addons_paths = tools.config['addons_path'].split(',')

        if selected_module:
            for addon_path in addons_paths:
                addon_path = addon_path.strip()
                module_path = os.path.join(addon_path, selected_module)

                for root, dirs, files in os.walk(module_path):
                    for file in files:
                        if file in ['__init__.py', '__manifest__.py']:
                            continue

                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)

                            result = subprocess.run(
                                ['flake8', file_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )

                            violations = result.stdout.strip().splitlines()

                            if violations:
                                for violation in violations:
                                    parts = violation.split(":", 3)
                                    if len(parts) >= 4:
                                        file_name = parts[0]
                                        line_number = parts[1]
                                        violation_message = parts[3]

                                        violations_list.append({
                                            'file_name': file_name,
                                            'line_number': line_number,
                                            'violation_message': violation_message
                                        })
                            else:
                                print(f"No violations found in {file_path}")

        return {'selected_module': selected_module,
                'violations_by_file': violations_list}

    # ///////////////////////////////////////////////

    @api.model
    def pep_standard_template(self):
        """Checks pep8 standards of installed modules, excluding selected modules"""

        module = self.env['ir.module.module'].search([('state', '=', 'installed')])
        installed_module_name = module.mapped('name')
        violations_list = {}

        # Getting addon paths
        addons_paths = tools.config['addons_path'].split(',')
        skipped_modules = []
        valid_modules = []

        # Looping through installed modules
        for module_name in installed_module_name:
            module_path = next(
                (os.path.join(path, module_name) for path in addons_paths if
                 os.path.isdir(os.path.join(path, module_name))),
                None
            )

            if module_path:
                path_parts = module_path.split(os.sep)

                # Skip modules in 'addons' directories
                if any(part == 'addons' for part in path_parts):
                    skipped_modules.append(module_name)
                else:
                    valid_modules.append(module_name)  # Append the valid module name


        # Process each valid module
        for custom_module in valid_modules:
            for addon_path in addons_paths:
                addon_path = addon_path.strip()
                module_path = os.path.join(addon_path, custom_module)

                # Traverse the module directory and process Python files
                for root, dirs, files in os.walk(module_path):
                    for file in files:
                        if file in ['__init__.py', '__manifest__.py']:  # Skip these files
                            continue

                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)

                            # Run flake8 to check PEP8 violations
                            result = subprocess.run(
                                ['flake8', file_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )

                            violations = result.stdout.strip().splitlines()

                            if violations:
                                for violation in violations:
                                    parts = violation.split(":", 3)
                                    if len(parts) >= 4:
                                        file_name = parts[0]
                                        line_number = parts[1]
                                        violation_message = parts[3]

                                        if custom_module not in violations_list:
                                            violations_list[custom_module] = []

                                        violations_list[custom_module].append({
                                            'module_name': custom_module,
                                            'file_name': file_name,
                                            'line_number': line_number,
                                            'violation_message': violation_message
                                        })
                            else:
                                print(f"No violations found in {file_path}")

        # print(violations_list)
        return {'module_name': valid_modules,
                'violations_by_file': violations_list}
    #
    # @api.model
    # def pep_standard_template(self):
    #     """Checks pep8 standards of installed modules, excluding selected modules"""
    #
    #     module = self.env['ir.module.module'].search([('state', '=', 'installed')])
    #     installed_module_name = module.mapped('name')
    #     violations_list = {}
    #     module_icons = {}  # Dictionary to store module icons
    #
    #     # Getting addon paths
    #     addons_paths = tools.config['addons_path'].split(',')
    #     skipped_modules = []
    #     valid_modules = []
    #
    #     # Looping through installed modules
    #     for module_name in installed_module_name:
    #         module_path = next(
    #             (os.path.join(path, module_name) for path in addons_paths if
    #              os.path.isdir(os.path.join(path, module_name))),
    #             None
    #         )
    #
    #         if module_path:
    #             path_parts = module_path.split(os.sep)
    #
    #             # Skip modules in 'addons' directories
    #             if any(part == 'addons' for part in path_parts):
    #                 skipped_modules.append(module_name)
    #             else:
    #                 valid_modules.append(module_name)  # Append the valid module name
    #
    #                 # Get module icon
    #                 manifest_path = os.path.join(module_path, '__manifest__.py')
    #                 if os.path.exists(manifest_path):
    #                     try:
    #                         with open(manifest_path, 'r') as f:
    #                             manifest_content = ast.literal_eval(f.read())
    #                             icon_path = manifest_content.get('icon', False)
    #                             if icon_path:
    #                                 full_icon_path = os.path.join(module_path, icon_path)
    #                                 if os.path.exists(full_icon_path):
    #                                     with open(full_icon_path, 'rb') as icon_file:
    #                                         icon_data = base64.b64encode(icon_file.read()).decode('utf-8')
    #                                         module_icons[module_name] = icon_data
    #                                 else:
    #                                     module_icons[module_name] = False
    #                             else:
    #                                 module_icons[module_name] = False
    #                     except Exception as e:
    #                         # _logger.error(f"Error reading manifest for module {module_name}: {e}")
    #                         module_icons[module_name] = False
    #
    #     print("valid_modules", valid_modules)
    #
    #     # Process each valid module
    #     for custom_module in valid_modules:
    #         for addon_path in addons_paths:
    #             addon_path = addon_path.strip()
    #             module_path = os.path.join(addon_path, custom_module)
    #
    #             # Traverse the module directory and process Python files
    #             for root, dirs, files in os.walk(module_path):
    #                 for file in files:
    #                     if file in ['__init__.py', '__manifest__.py']:  # Skip these files
    #                         continue
    #
    #                     if file.endswith('.py'):
    #                         file_path = os.path.join(root, file)
    #
    #                         # Run flake8 to check PEP8 violations
    #                         result = subprocess.run(
    #                             ['flake8', file_path],
    #                             stdout=subprocess.PIPE,
    #                             stderr=subprocess.PIPE,
    #                             text=True
    #                         )
    #
    #                         violations = result.stdout.strip().splitlines()
    #                         print("violations", violations)
    #
    #                         if violations:
    #                             for violation in violations:
    #                                 parts = violation.split(":", 3)
    #                                 if len(parts) >= 4:
    #                                     file_name = parts[0]
    #                                     line_number = parts[1]
    #                                     violation_message = parts[3]
    #
    #                                     if custom_module not in violations_list:
    #                                         violations_list[custom_module] = []
    #
    #                                     violations_list[custom_module].append({
    #                                         'module_name': custom_module,
    #                                         'file_name': file_name,
    #                                         'line_number': line_number,
    #                                         'violation_message': violation_message
    #                                     })
    #                         else:
    #                             print(f"No violations found in {file_path}")
    #
    #     print(violations_list)
    #     return {
    #         'module_name': valid_modules,
    #         'violations_by_file': violations_list,
    #         'module_icons': module_icons  # Add icons to the return value
    #     }
