/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


export class ServerTemplate extends Component {
setup() {
        super.setup();
        this.orm = useService('orm');
        this._fetchSystemMetrics();
        this._fetchMemoryMetrics();
        this._fetchProcessMemory();
        this._fetchDiskMemory();
        this._fetchConcurrentSession();
        this._systemMonitoring();
        this._CountFields();
        this._ModuleLoad();
        this._DatabaseMonitoring();
        this._DbMetricsMonitoring();
        this._exx();
        this._FileHealthMonitoring();
        this.state = useState({
            metrics : {},
            concurrent_metrics:{},
            server : {},
            quality_monitoring : {},
            module_naming : {},
            field : {},
            load_module : {},
            db_metrics : {},
            file_metrics : {},
            installed_modules : {},
            module : '',
            module_violations : {},
            memory_metrics : {},
            process_metrics : {},
            disk_metrics : {}
        });
    }

    async _fetchSystemMetrics() {
        this.orm.call("system.metrics", "get_system_metrics_data", [], {}).then((result) => {
            this.state.metrics = result
        });
    }

    async _fetchMemoryMetrics() {
        this.orm.call("system.metrics", "get_memory_metrics_data", [], {}).then((result) => {
            this.state.memory_metrics = result
        });
    }

    async _fetchProcessMemory() {
        this.orm.call("system.metrics", "get_process_memory_metrics_data", [], {}).then((result) => {
            this.state.process_metrics = result
        });
    }

    async _fetchDiskMemory() {
        this.orm.call("system.metrics", "get_disk_metrics_data", [], {}).then((result) => {
            this.state.disk_metrics = result
        });
    }
    async _exx() {
        this.orm.call("system.metrics", "get_odoo_edition_info", [], {}).then((result) => {
//            this.state.disk_metrics = result
        });
    }

    async _fetchConcurrentSession() {
            this.orm.call("database.metrics", "get_concurrent_session_count", [], {}).then((result) => {
                this.state.concurrent_metrics = result
            });
    }

    async _systemMonitoring() {
            this.orm.call("system.metrics", "get_server_uptime", [], {}).then((result) => {
                this.state.server = result
            });
    }

    async _CountFields() {
            this.orm.call("module.quality", "count_of_non_stored_fields", [], {}).then((result) => {
                this.state.field = result
            });
    }

    async _ModuleLoad() {
            this.orm.call("module.quality", "module_load_time", [], {}).then((result) => {
                this.state.load_module = result
            });
    }

    async _DatabaseMonitoring() {
            this.orm.call("module.quality", "modules_installed", [], {}).then((result) => {
            });
    }

    async _DbMetricsMonitoring() {
            this.orm.call("database.metrics", "collect_metrics", [], {}).then((result) => {
                this.state.db_metrics = result
                console.log("this.state.db_metrics",this.state.db_metrics)
            });
    }

    async _FileHealthMonitoring() {
            this.orm.call("database.metrics", "odoo_file_health", [], {}).then((result) => {
                this.state.file_metrics = result
            });
    }
    }

ServerTemplate.template = "odoo_health_report_tool.server_health_template"
registry.category('actions').add('server_template_tag', ServerTemplate);
