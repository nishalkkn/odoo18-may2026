/** @odoo-module **/
import { Layout } from "@web/search/layout";
import { Component,onWillUnmount, useRef, onWillStart} from "@odoo/owl";
import { loadJS,loadCSS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { NoteDialog } from "./note_popup"

export class CostcutCalendar extends Component {
    setup() {
        /** Initializes ORM and action services, references, and calls getAppointments to fetch initial data. */
        this.isComponentDestroyed = false;
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialogService = useService("dialog");
        this.CalendarDiv = useRef("daypilot")
        console.log('this.CalendarDiv', this.CalendarDiv)
        this.NavigatorDiv = useRef("navigator")
        this.EmployeesDiv = useRef("employees")
                this.employeeSearchRef = useRef("employeeSearchRef")
        onWillUnmount(() => {
            this.isComponentDestroyed = true;
        });
        onWillStart(async() => {
           await loadJS("https://cdn.jsdelivr.net/npm/@daypilot/daypilot-lite-javascript@3.30.0/daypilot-javascript.min.js");
           await loadJS("https://cdn.jsdelivr.net/npm/sweetalert2@11.14.4/dist/sweetalert2.all.min.js")
           await loadCSS("https://cdn.jsdelivr.net/npm/sweetalert2@11.14.4/dist/sweetalert2.min.css")
           this.getAppointments();
        })
    }
    async getAppointments() {
        /**
         * Fetches appointment data from the database, adjusts timezone offset,
         * formats start and end times, and sets up SweetAlert2 library for alerts.
         * Calls getEmployees to load staff data.
         */
        if (this.isComponentDestroyed) return; // Check if component is destroyed
        const now = new Date();
        const offset = now.getTimezoneOffset();
        const offsetHours = Math.floor(Math.abs(offset) / 60);
        const offsetMinutes = Math.abs(offset) % 60;
//        this.eventsData = await this.orm.searchRead('appointment.schedule', [], []);
        this.eventsData = await this.orm.searchRead('sale.order.line', [['is_appointment','=',true]], []);
        this.backColors = await this.orm.searchRead('scheduler.config',[['name','=','sale.order.line']],[])
        const offsetMilliseconds = (offsetHours * 60 + offsetMinutes) * 60 * 1000
        this.events = this.eventsData.map(event => {
            const newStart = new Date(new Date(event.time_from + 'Z').getTime() + offsetMilliseconds).toISOString();
            const newEnd = new Date(new Date(event.time_to + 'Z').getTime() + offsetMilliseconds).toISOString();
            const start = new Date(event.time_from + 'Z').toISOString();  // Interprets as UTC
            const end = new Date(event.time_to + 'Z').toISOString();
            const startTime = new Date(start).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
                timeZone: user.tz
            });
            const endTime = new Date(end).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
                timeZone: user.tz
            });
            const state = event.order_state ? event.order_state.charAt(0).toUpperCase() + event.order_state.slice(1) : 'Pending';
            return {
                id: event.id,
                text: `${event.partner_id[1] || 'No customer name'}\n${startTime} - ${endTime}\nStatus: ${state}\n${event.note || ""}`,
                start: new Date(new Date(event.time_from + 'Z').getTime() + offsetMilliseconds).toISOString(),
                end: new Date(new Date(event.time_to + 'Z').getTime() + offsetMilliseconds).toISOString(),
                resource: event.employee_id[0],
                backColor: this.backColors[0][event.order_state],
                tags: {
                    state: event.order_state
                }
            };
        });
      this.getEmployees();
    }
    async getEmployees() {
    /**
         * Fetches employee data, including names and profile images, and renders a
         * checkbox list in the EmployeesDiv to allow filtering of appointments by staff.
         */
        if (this.isComponentDestroyed) return; // Check if component is destroyed
        this.employees = await this.orm.searchRead('hr.employee', [['available_in_schedule','=',true]], ['name', 'image_1920']);
        const employeesDiv = this.EmployeesDiv.el;
        console.log('employeesDiv', employeesDiv)
        employeesDiv.innerHTML = '<h4>Staffs</h4>'; // Add a title
        this.employees.forEach(employee => {
            const employeeHTML = `
                <div class="employee-checkbox">
                    <input type="checkbox" id="employee-${employee.id}" data-id="${employee.id}" checked>
                    <label for="employee-${employee.id}">
                        ${`<img src="/web/image/hr.employee/${employee.id}/avatar_128" class="employee-image"
                                 style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #ffffff; margin-right: 10px;">`
                        }
                        ${employee.name}
                    </label>
                </div>
            `;
            employeesDiv.insertAdjacentHTML('beforeend', employeeHTML);
        });
        employeesDiv.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.filterEmployees());
        });
        this.renderCalendar();
    }
    async openWizard(startDate, endDate, employeeID, viewID) {
     /**
         * Opens a scheduling form with start and end dates and pre-selected
         * employee details. Displays form view for creating or editing an appointment.
         */
        // Convert startDate and endDate to Date objects
        const start = new Date(startDate);
        const end = new Date(endDate);
        const formattedStartDate = start.toISOString().slice(0, 19).replace('T', ' ');
        const formattedEndDate = end.toISOString().slice(0, 19).replace('T', ' ');
        const formViewID = await this.orm.search('ir.ui.view', [
            ['name', '=', 'appointment.schedule.wizard.view.form']
        ]);
        const lineFormViewID = await this.orm.search('ir.ui.view', [
            ['name', '=', 'sale.order.line.view.form.costcut']
        ]);
        var actionConfig = {
            name: "Appointment Schedule",
            res_model: "appointment.schedule",
            type: "ir.actions.act_window",
            target: "new",
            views: [
                [formViewID[0], "form"]
            ],
        };
        if (viewID) {
            actionConfig = {
            name: "Appointment Schedule",
            res_model: "sale.order.line",
            res_id: viewID,
            type: "ir.actions.act_window",
            target: "new",
            views: [
                [lineFormViewID[0], "form"]
            ],
        };
        } else {
            actionConfig.context = {
                default_order_line: [[0, 0, {
                    time_from: formattedStartDate,
                    time_to: formattedEndDate,
                    employee_id: employeeID
                }]]
            };
        }
        this.action.doAction(actionConfig);
    }
    async renderCalendar() {
        /**
         * Initializes and configures the DayPilot calendar with appointment events
         * and employee resources, and sets up event handlers for time range selection
         * and appointment movement with conflict checking.
         */
        const calendarElement = this.CalendarDiv.el;
        this.calendar = new DayPilot.Calendar(calendarElement, {
            viewType: "Resources",
            scale: "Hour",
            startDate: DayPilot.Date.today(),
            expanded: true,
            timeZone: user.tz,
            cellsAutoUpdated: true,
            durationBarVisible: false,
            cellDuration: this.backColors[0]['duration']*60,
//            businessBeginsHour: this.backColors[0]['time_from'],
//            businessEndsHour: this.backColors[0]['time_to'],
            headerHeight: 90,
            cellDuration: 15,
            columns: this.employees?.map(employee => ({
                name: employee.name,
                id: employee.id,
                width: 100,
                image: employee.image_1920 ? `data:image/jpeg;base64,${employee.image_1920}` : null, // Set to null if no image
            })),
            cellHeight: 50,
            events: this.events,
            onTimeRangeSelected: (args) => {
                this.openWizard(args.start, args.end, args.resource)
            },
//            onEventClick: (args) => {
//                console.log(args, "args")
//                this.openWizard(false, false, false, args.e.data.id)
//            },
            onBeforeHeaderRender: args => {
                // Check if the column has an image or needs the fallback icon
                const imageHTML =  `<img src="/web/image/hr.employee/${args.column.id}/avatar_128"
                             style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #ffffff; margin-right: 10px;" />`;
                args.header.html = `
                    <div style="display: flex; align-items: center;flex-wrap:wrap;">
                        ${imageHTML}
                        <span style="font-weight: bold; color: #333333;">
                            ${args.column.data.name}
                        </span>
                    </div>
                `;
            },
            contextMenu: new DayPilot.Menu({
                items: [
                    {
                        text: "Confirm",
                        onClick:async args => {
                            const eventRecord =await this.eventsData.find(event => event.id === args.source.id());
                            this.orm.call("sale.order.line","confirm_appointment", [eventRecord.id]).then(()=>{
                                this.action.doAction("soft_reload")
                            })
                        },
                        icon: "fa fa-check"
                    },
                    {
                        text: "Arrived",
                        onClick:async args => {
                            const eventRecord =await this.eventsData.find(event => event.id === args.source.id());
                            this.orm.call("sale.order.line","customer_arrived", [eventRecord.id]).then(()=>{
                                this.action.doAction("soft_reload")
                            })
                        },
                        icon: "fa fa-sign-in"
                    },
                    {
                        text: "No Show",
                        onClick:async args => {
                            const eventRecord = await this.eventsData.find(event => event.id === args.source.id());
                            this.orm.call("sale.order.line","customer_not_arrived", [eventRecord.id]).then(()=>{
                                this.action.doAction("soft_reload")
                            })
                        },
                        icon: "fa fa-ban"
                    },
                    {
                        text: "Payment",
                        onClick:async args => {
                            const eventRecord =await this.eventsData.find(event => event.id === args.source.id());
                        },
                        icon: "fa fa-money"
                    },
                    {
                        text: "Note",
                        onClick:async args => {
                            const eventRecord = await this.eventsData.find(event => event.id === args.source.id());
                            console.log(eventRecord, "Event")
                            console.log(this, "This")
                            this.dialogService.add(NoteDialog, {
                                initialNote: eventRecord.note || "",
                                save: async (noteText) => {
                                    // Save the note to the record
                                    await this.orm.write("sale.order.line", [eventRecord.id], {
                                        note: noteText
                                    });
                                    // Refresh the calendar if needed
                                    this.getAppointments();
                                },
                            });
                        },
                        icon: "fa fa-sticky-note-o"
                    },
                    {
                        text: "Edit",
                        onClick:async args => {
                            this.openWizard(false, false, false, args.source.data.id)
                        },
                        icon: "fa fa-edit"
                    },
                    {
                        text: "Reschedule",
                        onClick:async args => {
                            console.log('reschedule')
                        },
                        icon: "fa fa-refresh"
                    },
                    {
                        text: "Execute",
                        onClick:async args => {
                            const eventRecord = await this.eventsData.find(event => event.id === args.source.id());
                            this.orm.call("sale.order.line","service_started", [eventRecord.id]).then(()=>{
                                this.action.doAction("soft_reload")
                            })
                        },
                        icon: "fa fa-check"
                    },
                    {
                        text: "Print Receipt",
                        onClick:async args => {
                            console.log("print")
                        },
                        icon: "fa fa-print"
                    },
                    {
                        text: "Done",
                        onClick:async args => {
                            const eventRecord = await this.eventsData.find(event => event.id === args.source.id());
                            this.orm.call("sale.order.line","service_started", [eventRecord.id]).then(()=>{
                                this.action.doAction("soft_reload")
                            })
                        },
                        icon: "fa fa-check-circle-o"
                    },
                ],
                onShow: function(args) {
                //Menu items visibility based on state
                    if(args.source.data.tags.state !== 'booked'){
                        //item confirm
                        args.menu.items[0].hidden = true
                    }
                    if(args.source.data.tags.state !== 'confirm'){
                        //item arrived
                        args.menu.items[1].hidden = true
                    }
                    if(args.source.data.tags.state !== ('booked' || 'confirm') ){
                        //item no show
                        args.menu.items[2].hidden = true
                    }
                    if(args.source.data.tags.state !== 'done'){
                        //item payment
                        args.menu.items[3].hidden = true
                    }
                    if(args.source.data.tags.state in ['no_show','cancel','paid','done']){
                        //item edit
                        args.menu.items[5].hidden = true
                    }
                    if(args.source.data.tags.state in ['arrived', 'ongoing','paid','done']){
                        //Reschedule
                        args.menu.items[6].hidden = true
                    }
                    if(args.source.data.tags.state !== 'arrived'){
                        //Execute
                        args.menu.items[7].hidden = true
                    }
                    if(args.source.data.tags.state !== 'paid'){
                        //Print
                        args.menu.items[8].hidden = true
                    }
                }
            }),
            onBeforeEventRender: args => {
                args.data.areas = [
                    {
                        top: 4,
                        right: 4,
                        height: 20,  // Increase the height of the box
                        width: 20,   // Increase the width of the box
                        visibility: "Hover",
                        action: "ContextMenu",
                        style: "border: 1px solid #000000; cursor: pointer; display: flex; align-items: center; justify-content: center;", // Set border color to pure black
                        html: `<img src="/costcut/static/description/chevron.png" style="width: 80%; height: 80%;" />`
                    }
                ];
            },
            onEventMoved: async args => {
                const matchingEvents = this.events.filter(event =>
                    event.resource === args.newResource && event.id !== args.e.data.id // Exclude the event being moved
                );
                const newStartTime = new Date(args.newStart.value).getTime();
                const newEndTime = new Date(args.newEnd.value).getTime();
                const hasConflict = matchingEvents.some(event => {
                    const existingStart = new Date(event.start).getTime();
                    const existingEnd = new Date(event.end).getTime();
                    return (
                        (newStartTime < existingEnd && newEndTime > existingStart) || // Partial overlap
                        (newStartTime >= existingStart && newEndTime <= existingEnd) || // New event within existing event
                        (newStartTime <= existingStart && newEndTime >= existingEnd) // Existing event within new event
                    );
                });
                if (hasConflict) {
                    Swal.fire("Conflict", "This employee has a conflicting appointment at the selected time.", "error")
                        .then(() => {
                            this.getAppointments(); // Re-fetch data to refresh the calendar without a full page reload
                        });
                    args.preventDefault(); // Prevent the event move if there's a conflict
                    return;
                }
                const result = await this.orm.call('sale.order.line', 'event_drag', [args.e.data.id], {
                    employee_id: args.newResource,
                    start_time: args.newStart.value,
                    end_time: args.newEnd.value,
                });
                this.getAppointments();
            },
        });
        this.navBar = new DayPilot.Navigator(this.NavigatorDiv.el, {
            onTimeRangeSelected: args => {
                this.calendar.startDate = args.day;
                this.calendar.update({
                    startDate: args.day,
                })
            }
        })
        this.navBar.init();
        this.calendar.init();
    }
        filterEmployees() {
    /**
     * Filters displayed appointments based on selected employees and search query.
     * Updates the calendar with filtered events.
     */
    const searchQuery = this.employeeSearchRef.el.value.toLowerCase();
    const selectedEmployeeIds = Array.from(this.EmployeesDiv.el.querySelectorAll('input[type="checkbox"]:checked'))
        .map(checkbox => checkbox.dataset.id);

    const filteredEmployees = this.employees
        .filter(employee => {
            const matchesSearch = employee.name.toLowerCase().includes(searchQuery);
            const matchesCheckbox = selectedEmployeeIds.length === 0 || selectedEmployeeIds.includes(employee.id.toString());
            return matchesSearch && matchesCheckbox;
        })
        .map(employee => ({
            name: employee.name,
            id: employee.id,
            width: 100,
            image: employee.image_1920 ? `data:image/jpeg;base64,${employee.image_1920}` : "../helpers/img/default-image.jpg"
        }));

    this.calendar.startDate = DayPilot.Date.today();
    this.calendar.update({ columns: filteredEmployees });
    this.calendar.update();
}
}
CostcutCalendar.template = "costcut.CalendarController"
CostcutCalendar.components = {
    Layout,
    Dialog
}
//registry.category("actions").add("costcut_calendar", CostcutCalendar)
