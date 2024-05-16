from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate_property_type'
    _description = "Estate Managment Property Type"
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string="Sequence")
    property_ids = fields.One2many('estate_property', 'property_type_id', string='Properties')
    offer_ids = fields.One2many('estate_property_offer', 'property_id', string="Offers")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")

    """ Depends && Functions or Methods """

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)
            

    """ SQL Constraints """

    _sql_constraints = {
        ('unique_type_name', 'UNIQUE(name)', 'Property type name must be unique!')
    }