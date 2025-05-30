/** @odoo-module **/
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { CostCutCalendarFilterPanel } from "./filter_panel/calendar_filter_panel";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, useState, onMounted, onWillUpdateProps } from "@odoo/owl";

export class CostcutCalendarControllers extends CalendarController {
    static components = {
        ...CalendarController.components,
        FilterPanel: CostCutCalendarFilterPanel,
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = {
            ...this.state,
            employees: [],
        };

        onWillStart(() => this.loadEmployees());

    }

    onWillUpdateProps(nextProps) {
        super.onWillUpdateProps(nextProps);
    }

    get groupedEmployeeRecord() {
        const {records} = this.model.data;
        const activeRecords = [];
        for (const employee of this.state.employees) {
            const orderRecs = Object.values(records).filter(item => item?.rawRecord?.employee_id[0] === employee.id);
            if (!orderRecs.length) continue;
            orderRecs.sort((a, b) => a.rawRecord.id - b.rawRecord.id);
            activeRecords.push({
                employee: employee.name,
                id: employee.id,
                records: orderRecs
            });
        }
        activeRecords.sort((a, b) => a.id - b.id);
        return activeRecords
    }

    async loadEmployees() {
        try {
            const employees = await this.orm.searchRead(
                "hr.employee",
                [["available_in_schedule", "=", true]],
                ["id", "name", "avatar_128"]
            );
            console.log('employees1',employees)

            employees.sort((a, b) => a.id - b.id);

            this.state.employees = employees.map((record, idx) => ({
                id: record.id,
                name: record.name,
                avatarUrl: `/web/image/hr.employee/${record.id}/avatar_128`,
                isChecked: true,
    //            isBooked: idx % 2 === 0
            }));
            console.log('groupedEmployeeRecord111', this.groupedEmployeeRecord);
        } catch(error) {
            console.error('Failed to load employees:', error);
        }
    }

    toggleEmployee(empId) {
        this.state.employees = this.state.employees.map((employee) => ({
            ...employee,
            isChecked: employee.id === empId ? !employee.isChecked : employee.isChecked,
        }));
        this.model.load();
        console.log('groupedEmployeeRecord after loadEmployees:', this.groupedEmployeeRecord);
    }

    get filterPanelProps() {
        return {
            ...super.filterPanelProps,
            employees: this.state.employees,
            toggleEmployee:(empId) => this.toggleEmployee(empId),
        };
    }

    get rendererProps() {
        console.log("this",this)
        console.log("this.date",typeof this.date.c)
        const superProps = super.rendererProps;
        const { year, month, day } = this.date.c;
        const formattedDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        return {
            ...superProps,
            employees: this.state.employees,
            groupedEmployeeRecord: this.groupedEmployeeRecord,
            selectedDate: formattedDate,
        };
    }
}
