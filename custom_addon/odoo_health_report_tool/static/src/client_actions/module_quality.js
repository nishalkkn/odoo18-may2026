/** @odoo-module **/
import { Component, useRef, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


export class ModuleQuality extends Component {
    setup() {
        super.setup();
        // Initialize services
        this.orm = useService('orm');
        this.filterModule();
        this._moduleMonitoring();
        this._ModuleNaming();
        this._CountFields();
        this._pepStandardTemplate();
//        this.loadViolations();
        this.state = useState({
            field : {},
            installed_modules : {},
            module_violations : {},
            module : '',
            quality_monitoring : {},
            module_naming : {},
            template_standard : {}
        });

     onWillUnmount(async() => {
        this.filterModule2();
      });

    }

    async _moduleMonitoring() {
        this.orm.call("module.quality", "count_lines_of_code_in_modules", [], {}).then((result) => {
            this.state.quality_monitoring = result
        });
    }

    async filterModule() {
            this.orm.call("module.quality", "modules_installed", [], {}).then((result) => {
                this.state.installed_modules = result
                console.log("this.state.installed_modules ",this.state.installed_modules )

            });
    }

    async _CountFields() {
            this.orm.call("module.quality", "count_of_non_stored_fields", [], {}).then((result) => {
                this.state.field = result
            });
    }

    async _ModuleNaming() {
            this.orm.call("module.quality", "module_naming_conventions", [], {}).then((result) => {
                this.state.module_naming = result

            });
    }

//    async _pepStandardTemplate() {
//            this.orm.call("module.quality", "pep_standard_template", [], {}).then((result) => {
//                this.state.template_standard = result
//                console.log("template",result)
//
//            });
//    }

    async _pepStandardTemplate() {
        try {
            const result = await this.orm.call("module.quality", "pep_standard_template", [], {});
            this.state.template_standard = result;
            console.log("template", result);
        } catch (error) {
            console.error("Error fetching PEP standard template:", error);
        }
    }
    ///////////////////////////////////////////

//   async loadViolations() {
//        const result = await this.orm.call("module.quality", "pep_module_filter", [], {});
//        // Group violations by module
//        const moduleViolations = {};
//        result.violations_by_file.forEach(violation => {
//            const moduleName = violation.file_name.split('/')[0];
//            if (!moduleViolations[moduleName]) {
//                moduleViolations[moduleName] = [];
//            }
//            moduleViolations[moduleName].push(violation);
//        });
//        this.state.modules = moduleViolations;
//    }
//
//    selectModule(moduleName) {
//        this.state.selectedModule = this.state.selectedModule === moduleName ? null : moduleName;
//    }
//    }
    //
//    async reportPep8() {
//            const selected_module = this.state.module
//            console.log("selected_module",selected_module)
//            this.orm.call("odoo.health.report.wizard", "report_argument", [selected_module], {}).then((result) => {
//    ////            this.state.module_violations = result
//    ////                    console.log("updated",this.state.module_violations)
//    //
//            });
//    }

//    async generateReport() {
//        try {
//            const action = await this.orm.call(
//                'report.odoo_health_report_tool.odoo_health_report',
//                'create_report_action',
//                [],
//                {
//                    data: {
//                        website: true,  // or false based on your needs
//                        server: true,   // or false based on your needs
//                        module_quality: true
//                    },
//                    context: {
//                        ...this.env.context,
//                        selected_module: this.state.module,
//                        module_violations: this.state.module_violations
//                    }
//                }
//            );
//            await this.action.doAction(action);
//        } catch (error) {
//            console.error("Error generating report:", error);
//        }
//    }

      async updateModule() {
            const selected_module = this.state.module
            console.log("selected_module",selected_module)
            this.orm.call("module.quality", "pep_module_filter", [selected_module], {}).then((result) => {
                this.state.module_violations = result
                        console.log("updated",this.state.module_violations)

            });
    }
    //
    async reportPep8() {
            const selected_module = this.state.module
            console.log("selected_module",selected_module)
            this.orm.call("odoo.health.report.wizard", "report_argument", [selected_module], {}).then((result) => {
    ////            this.state.module_violations = result
    ////                    console.log("updated",this.state.module_violations)
    //
            });
    }

    async generateReport() {
        try {
            const action = await this.orm.call(
                'report.odoo_health_report_tool.odoo_health_report',
                'create_report_action',
                [],
                {
                    data: {
                        website: true,  // or false based on your needs
                        server: true,   // or false based on your needs
                        module_quality: true
                    },
                    context: {
                        ...this.env.context,
                        selected_module: this.state.module,
                        module_violations: this.state.module_violations
                    }
                }
            );
            await this.action.doAction(action);
        } catch (error) {
            console.error("Error generating report:", error);
        }
    }

    async filterModule2(){
            await this.updateModule();
            await this.generateReport();

    }
    }

ModuleQuality.template = "odoo_health_report_tool.module_quality_template"
registry.category('actions').add('module_quality_tag', ModuleQuality);