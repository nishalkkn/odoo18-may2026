/** @odoo-module **/

import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { registry } from "@web/core/registry";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class EmployeeNameCalendarRenderer extends CalendarRenderer {
  setup() {
        super.setup();
        this.orm = useService("orm");
        onWillStart(async () => {
            const current_company_id = this.env.services.company.currentCompany.id
            this.employees = await this.orm.searchRead("hr.employee", [], ["name"])
            console.log("👥 Employees:", this.employees);
        });
    }


    renderSidebar() {
        console.log("🧩 renderSidebar called");
    }
}

registry.category("views").add("calendar_with_employees", {
    ...registry.category("views").get("calendar"),
    Renderer: EmployeeNameCalendarRenderer,
});
