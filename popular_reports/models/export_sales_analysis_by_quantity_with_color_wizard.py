from odoo import models, fields
from datetime import datetime, timedelta
from odoo import models, fields, api
 
class PopularReportMethods(models.TransientModel):
    _inherit = "wizard.popular.reports"
    
    # Export Sales Analysis Report by Quantity with Colors
    # This function processed the data of onhand product and put them on report.
    def print_report_export_sales_analysis_by_quantity_with_colors(self):
        domain = [
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal') 
        ]

        if self.products:
            domain.append(('product_id', 'in', self.products.ids))
        if self.product_cat:
            domain.append(('product_id.categ_id', '=', self.product_cat.id))

        if self.start_date:
            domain.append(('in_date', '<=', self.start_date))

        quants = self.env['stock.quant'].search(domain)
        stock_move_env = self.env['stock.move']
        product_data = {}

        for quant in quants:
            product = quant.product_id
            product_id = product.id

            if product_id not in product_data:
                product_data[product_id] = {
                    'over_1_year': 0,
                    'over_1.5_year': 0,
                    'over_2_year': 0,
                    'total': 0.0,
                }

            oldest_move = stock_move_env.search([
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('location_dest_id.usage', '=', 'internal'),
                ('date', '<=', self.start_date) 
            ], order="date asc", limit=1)

            stock_entry_date = oldest_move.date.date() if oldest_move else self.start_date
            delta = self.start_date - stock_entry_date
            age_years = delta.days / 365.0

            if age_years >= 2:
                product_data[product_id]['over_2_year'] += quant.quantity
                product_data[product_id]['total'] += quant.quantity
            elif age_years >= 1.5:
                product_data[product_id]['over_1.5_year'] += quant.quantity
                product_data[product_id]['total'] += quant.quantity
            elif age_years >= 1:
                product_data[product_id]['over_1_year'] += quant.quantity
                product_data[product_id]['total'] += quant.quantity

        report_data = []
        for product_id, data in product_data.items():
            product = self.env['product.product'].browse(product_id)
            report_data.append({
                'product_name': product.display_name,
                'over_1_year': data['over_1_year'],
                'over_1.5_year': data['over_1.5_year'],
                'over_2_year': data['over_2_year'],
                'total': data['total']
            })

        return self.env.ref('popular_reports.action_report_sales_analysis_by_quantity_with_colors').report_action(
            self, 
            data={'report_data': report_data}
        )