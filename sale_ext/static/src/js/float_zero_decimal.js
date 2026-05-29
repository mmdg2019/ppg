import { FloatField } from "@web/views/fields/float/float_field";
import { registry } from "@web/core/registry";

export class FloatZeroDecimalField extends FloatField {

    get formattedValue() {
        const value = this.props.record.data[this.props.name];

        if (value === undefined || value === null) {
            return "";
        }

        return Math.trunc(value).toFixed(2);
    }
}

registry.category("fields").add(
    "float_zero_decimal",
    {
        ...FloatField,
        component: FloatZeroDecimalField,
    }
);