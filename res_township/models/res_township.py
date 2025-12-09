from odoo import models, fields, api

class Township(models.Model):
    _name = 'res.township'
    _description = 'Township'

    name = fields.Char(string='Township Name', required=True)
    code = fields.Char(string='Township Code', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True, default=lambda self: self.env['res.country'].search([('code', '=', 'MM')], limit=1))
    state_id = fields.Many2one('res.country.state', string='State', required=True, domain="[('country_id', '=', country_id)]")
    city_id = fields.Many2one('res.city', string='City', required=True, domain="[('state_id', '=', state_id)]")
    active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'The township code must be unique.'),
        ('unique_name_state', 'UNIQUE(name, state_id)', 'The township name must be unique within the same state.'),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.code})"
            if record.state_id:
                name += f" - {record.state_id.name}"
            if record.country_id:
                name += f" ({record.country_id.name})"
            result.append((record.id, name))
        return result   

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        return {'domain': {'state_id': []}}
    
    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
        return {'domain': {'city_id': []}}
    
    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.state_id = self.city_id.state_id
            self.country_id = self.city_id.country_id