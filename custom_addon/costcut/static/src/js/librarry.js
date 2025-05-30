///** @odoo-module **/
//import publicWidget from "@web/legacy/js/public/public_widget";
////import { AppointmentScheduler } from "@costcut/appointment_schedule";
//
//publicWidget.registry.AppointmentScheduler = publicWidget.Widget.extend({
//    selector: "#scheduler-container", // The target container
//    start: function () {
//        console.log("Appointment Scheduler Widget Loaded!");
//
//        if (!this.$el.length) {
//            console.error("Scheduler container not found!");
//            return;
//        }
//
//        AppointmentScheduler.init("scheduler-container", {
//            interval: 15,
//            startTime: "09:00",
//            endTime: "17:00",
//            employees: [
//                { id: "1", name: "John Doe" },
//                { id: "2", name: "Jane Smith" }
//            ],
//            onAppointmentCreate: function (appointment) {
//                console.log("Appointment created:", appointment);
//            },
//        });
//    },
//});
