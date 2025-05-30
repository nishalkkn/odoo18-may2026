/** @odoo-module */
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class NoteDialog extends Component {
    static template = "costcut.NoteDialog";
    static components = { Dialog }
    static props = {
        close: Function,
        save: Function,
        initialNote: String,
    };

    setup() {
        this.state = {
            note: this.props.initialNote || "",
        };
    }

    onSave() {
        this.props.save(this.state.note);
        this.props.close();
    }
}
registry.category("actions").add("note_dialog", NoteDialog);