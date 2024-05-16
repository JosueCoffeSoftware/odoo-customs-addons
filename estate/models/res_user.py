from odoo import fields, models, api

class ResUsers(models.Model):
    _name = 'res_user'
    _inherit = 'estate_property'

    property_ids = fields.One2many(
        comodel_name = 'estate_property',
        inverse_name = 'seller_id',
        string = 'Properties',
        domain = lambda self: self._get_available_properties_domain()
    )

    @api.model
    def _get_available_properties_domain(self):
        return [('state', 'in', ['new', 'offer_received'])]