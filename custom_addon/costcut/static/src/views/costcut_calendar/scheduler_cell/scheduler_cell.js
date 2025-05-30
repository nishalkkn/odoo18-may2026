/** @odoo-module **/
import { useState } from "@odoo/owl";

export class SchedulerCell extends owl.Component {
    static template = "costcut.SchedulerCell";
//    static props = {
//        employee: Object,
//        slotStart: String,
//    }

    setup() {
        super.setup();
        console.log('Employee', this)
    }

    get records() {
        return this.props.employee.records
    }

//    get sortedRecord() {
//        const {start_time_obj, end_time_obj} = this.props.slot
//        return this.records.filter(item => {
//          const {hour, minute} = item.start.c
//          return (start_time_obj.hour >= hour && start_time_obj.minute >= minute) && (hour <= end_time_obj.hour && minute < end_time_obj.minute)
//        })
//    }
    get sortedRecord() {
        const { start_time_obj, end_time_obj } = this.props.slot;

        // Convert start_time_obj and end_time_obj to minutes for easier comparison
        const startTimeInMinutes = start_time_obj.hour * 60 + start_time_obj.minute;
        const endTimeInMinutes = end_time_obj.hour * 60 + end_time_obj.minute;

        return this.records.filter(item => {
            const { hour, minute } = item.start.c;

            // Convert the record's start time into minutes
            const recordStartTimeInMinutes = hour * 60 + minute;
            const recordEndTimeInMinutes = recordStartTimeInMinutes + 5; // Record lasts 5 minutes

            // We will loop through each 5-minute time window from start_time_obj to end_time_obj
            let recordMatches = false;

            for (let slotStart = startTimeInMinutes; slotStart < endTimeInMinutes; slotStart += 5) {
                const slotEnd = slotStart + 5;
                // Check if the record falls within this slot
                if (
                    (recordStartTimeInMinutes < slotEnd && recordEndTimeInMinutes > slotStart) // Overlapping with the time slot
                ) {
                    recordMatches = true;
                    break; // If we find a match, no need to continue checking further slots
                }
            }

            return recordMatches;
        });
    }

}
