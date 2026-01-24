from odoo import models, fields, api
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime


class ExportCarWayWizard(models.TransientModel):
    _name = "export.car.way.wizard"
    _description = "Export Car Way to Excel Wizard"

    file_name = fields.Char(
        string="File Name",
        default=lambda self: f'car_way_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
    )

    def export_to_excel(self):
        sale_orders = self.env["sale.order"].browse(
            self.env.context.get("active_ids", [])
        )

        # Grouping by Township
        grouped = {}
        for order in sale_orders:
            car_number = order.car_number_id.name or ""
            if car_number not in grouped:
                grouped[car_number] = []
            grouped[car_number].append(order)

        # Start Excel creation
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Car Way Assignments")

        # Styles
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "white",
                "font_color": "black",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )

        group_header = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D9D9D9",
                "font_color": "black",
                "align": "left",
                "border": 1,
            }
        )

        text_format = workbook.add_format({"border": 1})
        number_format = workbook.add_format({"border": 1, "num_format": "#,##0"})

        # Headers
        headers = [
            "Order Reference",
            "Customer",
            "",
            "Order Date",
            "Delivery Assign Status",
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 22)

        row = 1

        # Write data with township grouping
        for car_number, orders in grouped.items():
            # car_size = ""
            # car_ton = ""
            # car_length = ""
            # car_width = ""
            # car_height = ""
            # if orders and orders[0].car_number_id:
            #     car = orders[0].car_number_id
            #     if hasattr(car, 'car_size'):
            #         car_size = car.car_size
            #     if hasattr(car, 'car_ton'):
            #         car_ton = car.car_ton
            #     if hasattr(car, 'car_length'):
            #         car_length = car.car_length
            #     if hasattr(car, 'car_width'):
            #         car_width = car.car_width
            #     if hasattr(car, 'car_height'):
            #         car_height = car.car_height
            # group_info = f"Car Number: {car_number} ({len(orders)}) \ Size: {car_size} \ Ton: {car_ton} \ Length: {car_length} \ Width: {car_width} \ Height: {car_height}"
            group_info = f"Car Number: {car_number} ({len(orders)})"
            # ---- Township Group Row ----
            worksheet.merge_range(
                row, 0, row, 4,group_info , group_header
            )
            row += 1

            # ---- Order Rows ----
            for order in orders:
                worksheet.write(row, 0, order.name or "", text_format)
                worksheet.merge_range(row, 1, row, 2, order.partner_id.name or "", text_format)

                worksheet.write(
                    row,
                    3,
                    (
                        order.date_order.strftime("%Y-%m-%d %H:%M:%S")
                        if order.date_order
                        else ""
                    ),
                    text_format,
                )

                worksheet.write(
                    row,
                    4,
                    dict(order._fields["delivery_assign_status"].selection).get(
                        order.delivery_assign_status, ""
                    ),
                    text_format,
                )
                row += 1

        # Autofilter
        # worksheet.autofilter(0, 0, row - 1, len(headers) - 1)

        # Save Excel
        workbook.close()
        output.seek(0)
        excel_data = base64.b64encode(output.read())

        attachment = self.env["ir.attachment"].create(
            {
                "name": self.file_name,
                "datas": excel_data,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "res_model": "sale.order",
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
            "close": True,
        }
