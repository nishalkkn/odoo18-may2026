/** @odoo-module **/
import { CalendarFilterPanel } from "@web/views/calendar/filter_panel/calendar_filter_panel";
import { useState } from "@odoo/owl";

export class CostCutCalendarFilterPanel extends CalendarFilterPanel {
    static template = "costcut.CostCutCalendarFilterPanel";

    static props = {
        ...CalendarFilterPanel.props,
        employees: { type: Array, optional: true },
        toggleEmployee: { type: Function, optional: true },
    };

    setup() {
        super.setup();
    }

}
