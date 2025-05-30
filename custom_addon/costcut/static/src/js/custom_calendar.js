/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class CustomCalendar extends Component {
    setup() {
        onMounted(() => {
            console.log("Custom Calendar mounted!");
            // init logic here
        });
    }

    static template = "costcut.CustomCalendarTemplate";
}

// Register the action
registry.category("actions").add("custom_calendar_js", CustomCalendar);
