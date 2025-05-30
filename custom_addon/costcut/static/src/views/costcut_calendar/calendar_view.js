/** @odoo-module **/

import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CostcutCalendarControllers } from './calendar_controller';
import { CostcutCalendarRenderer } from './calendar_renderer';

const attendeeCalendarView = {
    ...calendarView,

    Controller: CostcutCalendarControllers,
    Renderer: CostcutCalendarRenderer,

};

registry.category("views").add("cost_extended_calendar", attendeeCalendarView);

