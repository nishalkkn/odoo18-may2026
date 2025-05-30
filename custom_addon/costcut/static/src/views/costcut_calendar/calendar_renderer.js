import { registry } from "@web/core/registry";
import { AttendeeCalendarRenderer } from "@calendar/views/attendee_calendar/attendee_calendar_renderer";
import { calendarView } from "@web/views/calendar/calendar_view";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { onWillStart, useState, onWillUpdateProps, useRef, onMounted } from "@odoo/owl";
import { SchedulerCell } from "./scheduler_cell/scheduler_cell";
import { CostcutCalendarControllers } from './calendar_controller';

export class CostcutCalendarRenderer extends owl.Component {
    static template = "costcut.CostcutCalendarRenderer";
    static components = {
        SchedulerCell,
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.rootTable = useRef('calendar-table');
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            timeslots: [],
        });

        onWillStart(async () => {
            const config = await this.orm.call("scheduler.config", "get_scheduler_config", []);
            const timeslots = this.calculateTimeSlots(config.time_from, config.time_to);
            this.state.timeslots = timeslots;
        });

        onMounted(() => {
            this.addEventListener();
            // Initialize the scheduler
            this.markExistingAppointments();
        })
    }

    markExistingAppointments() {
        const slots = this.rootTable.el.querySelectorAll("td:has(.appointment-slot)");
        slots.forEach(slot => {
            const employeeId = slot.getAttribute("data-employee");
            if (employeeId && this.getScheduledTime(
                Number(employeeId),
                this.getTimeFromSlot(slot),
                this.props.groupedEmployeeRecord
            )) {

                slot.classList.add("scheduled");
            }
        });
    }

    addEventListener = () => {
    let isDragging = false;
    let startTime = null;
    let endTime = null;
    let initialSlot = null;
    let selectedSlots = new Set();
    let selectedEmployee = null;
    let hasOverlap = false;

    const clearSelection = () => {
        selectedSlots.forEach(slot => {
            slot.classList.remove("selecting");
            slot.classList.remove("overlap-indicator");
        });
        selectedSlots.clear();
        hasOverlap = false;
    };

    const checkOverlap = (slot, employeeId) => {
        return this.getScheduledTime(
            Number(employeeId),
            this.getTimeFromSlot(slot),
            this.props.groupedEmployeeRecord
        );
    };

    const updateSelection = (currentSlot) => {
        clearSelection();

        const slots = Array.from(this.rootTable.el.querySelectorAll("td:has(.appointment-slot)"));
        const currentIndex = slots.indexOf(currentSlot);
        const initialIndex = slots.indexOf(initialSlot);

        if (currentIndex !== -1 && initialIndex !== -1) {
            const lowerIndex = Math.min(currentIndex, initialIndex);
            const upperIndex = Math.max(currentIndex, initialIndex);

            if (currentIndex < initialIndex) {
                startTime = this.getTimeFromSlot(slots[currentIndex]);
                endTime = this.getTimeFromSlot(slots[initialIndex]);
            } else {
                startTime = this.getTimeFromSlot(slots[initialIndex]);
                endTime = this.getTimeFromSlot(slots[currentIndex]);
            }

            hasOverlap = false;
            for (let i = lowerIndex; i <= upperIndex; i++) {
                const slot = slots[i];
                const slotEmployeeId = slot.getAttribute("data-employee");

                if (slotEmployeeId === selectedEmployee) {
                    if (checkOverlap(slot, selectedEmployee)) {
                        hasOverlap = true;
                        slot.classList.add("overlap-indicator");
                    } else {
                        slot.classList.add("selecting");
                    }
                    selectedSlots.add(slot);
                }
            }

            if (hasOverlap) {
                selectedSlots.forEach(slot => {
                    slot.classList.remove("selecting");
                    slot.classList.add("overlap-indicator");
                });
            }
        }
    };

    this.rootTable.el.querySelectorAll("td:has(.appointment-slot)").forEach((slot) => {
        slot.addEventListener("mousedown", (event) => {
            const targetSlot = event.target.closest("td");
            const employeeId = targetSlot.getAttribute("data-employee");

            if (checkOverlap(targetSlot, employeeId)) {
                this.notification.add(
                    `This time slot is already scheduled for this employee.`,
                    { type: "warning" }
                );
                return;
            }

            isDragging = true;
            initialSlot = targetSlot;
            startTime = this.getTimeFromSlot(targetSlot);
            endTime = startTime;
            selectedEmployee = employeeId;
            clearSelection();
            targetSlot.classList.add("selecting");
            selectedSlots.add(targetSlot);
        });

        slot.addEventListener("mouseenter", (event) => {
            if (isDragging && event.target.getAttribute("data-employee") === selectedEmployee) {
                updateSelection(event.target);
            }
        });

        // Add click event listener
        slot.addEventListener("click", async (event) => {
            const targetSlot = event.target.closest("td");
            const employeeId = targetSlot.getAttribute("data-employee");
            const slotTime = this.getTimeFromSlot(targetSlot);

            if (this.getScheduledTime(Number(employeeId), slotTime, this.props.groupedEmployeeRecord)) {
                // Get the appointment details
                const appointment = this.getAppointmentDetails(Number(employeeId), slotTime);

                if (appointment) {
                    // Open the form view to display or edit the appointment details
                    this.action.doAction({
                        name: "Appointment Schedule",
                        res_model: "appointment.schedule",
                        type: "ir.actions.act_window",
                        res_id: appointment.id, // Assuming the appointment object has an id property
                        views: [[false, "form"]],
                        target: "new",
                    });
                } else {
                    // If appointment is not found, refresh the groupedEmployeeRecord
                    await this.refreshGroupedEmployeeRecord();
                    const refreshedAppointment = this.getAppointmentDetails(Number(employeeId), slotTime);
                    if (refreshedAppointment) {
                        this.action.doAction({
                            name: "Appointment Schedule",
                            res_model: "appointment.schedule",
                            type: "ir.actions.act_window",
                            res_id: refreshedAppointment.id,
                            views: [[false, "form"]],
                            target: "new",
                        });
                    } else {
                        this.notification.add(
                            "Appointment not found.",
                            { type: "warning" }
                        );
                    }
                }
            }
        });
    });

    document.addEventListener("mouseup", () => {
        if (isDragging && selectedSlots.size > 0) {
            isDragging = false;

            if (!hasOverlap) {
                const date = this.props.selectedDate;
                const start = new Date(`${date} ${startTime}`);
                const end = new Date(`${date} ${endTime}`);

                if (start <= end) {
                    const formattedStartDate = start.toISOString().slice(0, 19).replace('T', ' ');
                    const formattedEndDate = end.toISOString().slice(0, 19).replace('T', ' ');

                    this.action.doAction({
                        name: "Appointment Schedule",
                        res_model: "appointment.schedule",
                        type: "ir.actions.act_window",
                        target: "new",
                        views: [[false, "form"]],
                        context: {
                            default_order_line: [[0, 0, {
                                time_from: formattedStartDate,
                                time_to: formattedEndDate,
                                employee_id: Number(selectedEmployee),
                            }]],
                        }
                    });
                }
            } else {
                this.notification.add(
                    "Cannot schedule over existing appointments for this employee.",
                    { type: "warning" }
                );
            }
            clearSelection();
        }
    });
};

getAppointmentDetails(employeeId, slotTime) {
    // Get the appointment details based on employeeId and slotTime
    const employeeRecords = this.props.groupedEmployeeRecord?.filter(record => record.id === employeeId);
    for (const employeeRecord of employeeRecords || []) {
        for (const record of employeeRecord.records || []) {
            const { start, end, id } = record;
            const checkTime = new Date(`${this.props.selectedDate} ${slotTime}`);
            if (checkTime >= start && checkTime <= end) {
                return { id, start, end }; // Return the appointment details
            }
        }
    }
    return null;
}

refreshGroupedEmployeeRecord = async () => {
    // Fetch the latest groupedEmployeeRecord from the server
    try {
        const config = await this.orm.call("scheduler.config", "get_scheduler_config", []);
        const timeslots = this.calculateTimeSlots(config.time_from, config.time_to);
        this.state.timeslots = timeslots;

        // Fetch the latest groupedEmployeeRecord
        const groupedEmployeeRecord = await this.orm.call("appointment.schedule", "search_read", [
            [], // Domain
            ["id", "employee_id", "start", "end"] // Fields
        ]);
        this.props.groupedEmployeeRecord = groupedEmployeeRecord;
    } catch (error) {
        console.error("Error refreshing groupedEmployeeRecord:", error);
        this.notification.add(
            "Failed to refresh appointment data.",
            { type: "danger" }
        );
};

getTimeFromSlot = (slotElement) => {
    const row = slotElement.closest("tr");
    return row ? row.querySelector(".time-slot").textContent.trim() : null;
};

getScheduledTime(employeeId, slot, groupedEmployeeRecord) {
    const checkTime = new Date(`${this.props.selectedDate} ${slot}`);
    const employeeRecords = groupedEmployeeRecord?.filter(record => record.id === employeeId);
    for (const employeeRecord of employeeRecords || []) {
        for (const record of employeeRecord.records || []) {
            const { start, end } = record;
            if (checkTime >= start && checkTime <= end) {
                return true;
            }
        }
    }
    return false;
};

calculateTimeSlots(startTime, endTime) {
    const timeslots = [];
    const slotDurationMinutes = 15;

    const toMinutes = (time) => Math.floor(time) * 60 + (time % 1) * 60;
    const toTimeFormat = (minutes) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        const ampm = hours >= 12 ? "PM" : "AM";
        const formattedHours = hours % 12 === 0 ? 12 : hours % 12;
        return `${formattedHours}:${mins.toString().padStart(2, "0")} ${ampm}`;
    };

    let currentMinutes = toMinutes(startTime);
    const endMinutes = toMinutes(endTime);

    while (currentMinutes < endMinutes) {
        const start = toTimeFormat(currentMinutes);
        const end = toTimeFormat(currentMinutes + slotDurationMinutes);
        const start_time_obj = {
            hour: Math.floor(currentMinutes / 60),
            minute: currentMinutes % 60
        };
        const end_time_obj = {
            hour: Math.floor((currentMinutes + slotDurationMinutes) / 60),
            minute: (currentMinutes + slotDurationMinutes) % 60
        };

        timeslots.push({ start, end, start_time_obj, end_time_obj });
        currentMinutes += slotDurationMinutes;
    }

    return timeslots;
};

getFilteredEmpRecord(records, startTime) {
    return {};
}
}
