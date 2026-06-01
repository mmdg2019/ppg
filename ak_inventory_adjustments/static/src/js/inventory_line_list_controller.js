import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";

export class InventoryLineListController extends ListController {
   
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    get inventoryId() {
        return this.props.context?.active_id || false;
    }

    async validatedInventoryAdjust() {
        // console.log("***Validating Inventory Adjustment***");
        if (this.model.root.editedRecord) {
            await this.model.root.save();
        }

        if (!this.inventoryId) {
            this.notification.add(_t("No active inventory id found."), {
                type: "warning",
            });
            return;
        }

        try {
            const res = await this.orm.call(
                "stock.inventory",
                "action_validate",
                [[this.inventoryId]]
            );
        } catch (error) {
            this.notification.add(
                _t("The inventory has been validated."),
                {
                    type: "warning",
                }
            );
            window.history.back();
        }

        // const res = await this.orm.call(
        //     "stock.inventory",
        //     "action_validate",
        //     [[this.inventoryId]]
        // );

        // if (res && typeof res === "object") {
        //     await this.action.doAction(res);
        // } else {
        //     this.notification.add(
        //         _t("The inventory has been validated."),
        //         { type: "success" }
        //     );

        //     window.history.back();
        // }
    }

}

export const InventoryLineListtView = {
    ...listView,
    Controller: InventoryLineListController,
    buttonTemplate: "ak_inventory_adjustments.ValidatedInventoryAdjust.Buttons",
};

registry.category("views").add("validated_inventory_adjust", InventoryLineListtView);
