from odoo import models, fields, api


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    date_deadline = fields.Datetime(
        'Deadline',
        copy=False,
        store=True,
        readonly=False,
        help="Informative date allowing to define when the manufacturing order should be processed at the latest to fulfill delivery on time.",
    )

    # @api.model
    # def create(self, vals):
    #     # Check if date_deadline is in vals and ensure it's set correctly
    #     if 'date_deadline' in vals:
    #         vals['date_deadline'] = vals['date_deadline']  # Optionally modify this value as needed
    #     return super(ManufacturingOrder, self).create(vals)
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get('date_deadline'):
                vals['date_deadline'] = vals['date_deadline']
        return super(ManufacturingOrder, self).create(vals_list)
            