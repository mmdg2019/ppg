/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";
import { formatDate } from "@web/core/l10n/dates";
import { formatDateTime } from "@web/core/l10n/dates";
import { ListRenderer } from "@web/views/list/list_renderer";


//-------------------------------------------------------------------------
// Form/Wizard Form Views
//-------------------------------------------------------------------------
patch(DateTimeField.prototype, {
    getFormattedValue(valueIndex, numeric = true) { // numeric = false >> Jan 31, numeric = true >> 31/01
        const values = this.values;
        const value = values[valueIndex];
        if (!value) {
            return "";
        }
        const { showSeconds, showTime } = this.props;
        if (this.field.type === "date") {
            return formatDate(value, { numeric });
        } else {
            const showDate =
                !showTime || valueIndex !== 1 || !values[0] || !values[0].hasSame(value, "day");
            return formatDateTime(value, {
                numeric,
                showSeconds,
                showTime,
                showDate,
            });
        }
    }
});


//-------------------------------------------------------------------------
// List/Kanban Views
//-------------------------------------------------------------------------
const formatters = registry.category("formatters");
formatters.add("datetime", (value, options = {}) => {
    return value ? formatDateTime(value, { numeric : true }) : "";
}, { force: true });

formatters.add("date", (value, options = {}) => {
    return value ? formatDate(value, { numeric : true }) : "";
}, { force: true });


//-------------------------------------------------------------------------
// List Views: for cases with enable_formatting=false
//-------------------------------------------------------------------------
patch(ListRenderer.prototype, {
    getFormattedValue(column, record) {
        const fieldName = column.name;
        const value = record.data[fieldName];
        if (column.fieldType === "date") {
            return value ? formatDate(value, { numeric : true }) : "";
        } 
        if (column.fieldType === "datetime") {
            return value ? formatDateTime(value, { numeric : true }) : "";
        }
        return super.getFormattedValue(column, record);
    },
});
