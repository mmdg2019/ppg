from odoo import models, fields
from datetime import datetime, timedelta
from odoo import models, fields, api
 
class PopularReportMethods(models.TransientModel):
    _inherit = "wizard.popular.reports"
    
    # Export Sales Analysis Report by Quantity with Colors
    # This function processed the data of onhand product and put them on report.
    def print_report_export_sales_analysis_by_quantity_with_colors(self):
        domain = [
            ('move_id.state', '=', 'done'),  
            ('location_dest_id.usage', '=', 'internal'),  
            ('date', '<=', self.start_date)  
        ]
        if self.products:
                domain.append(('product_id', 'in', self.products.ids))

        move_lines = self.env['stock.move.line'].search(domain, order="date asc")
        product_data = {}

        for move_line in move_lines:
            product = move_line.product_id
            product_id = product.id

            if product_id not in product_data:
                product_data[product_id] = {
                    'over_1_year': 0,
                    'over_1.5_year': 0,
                    'over_2_year': 0,
                    'remaining_qty': product.with_context({'location': move_line.location_dest_id.id}).qty_available  
                }

            remaining_qty = product_data[product_id]['remaining_qty']
            if remaining_qty <= 0: 
                continue  

            move_date = move_line.date.date()  
            delta = self.start_date - move_date
            age_years = delta.days / 365.0  

            if age_years < 1:
                continue  

            allocated = min(remaining_qty, move_line.qty_done)  

            if age_years > 2:
                product_data[product_id]['over_2_year'] += allocated
            elif age_years > 1.5:
                product_data[product_id]['over_1.5_year'] += allocated
            elif age_years > 1:
                product_data[product_id]['over_1_year'] += allocated
            product_data[product_id]['remaining_qty'] -= allocated  
            
        report_data = []
        for product_id, data in product_data.items():
            product = self.env['product.product'].browse(product_id)

            total = data['over_1_year'] + data['over_1.5_year'] + data['over_2_year']

            if total > 0:
                report_data.append({
                    'product_name': product.display_name,
                    'over_1_year': data['over_1_year'],
                    'over_1.5_year': data['over_1.5_year'],
                    'over_2_year': data['over_2_year'],
                    'total': total,
                })

        return self.env.ref('popular_reports.action_report_sales_analysis_by_quantity_with_colors').report_action(
            self, 
            data={'report_data': report_data}
        )