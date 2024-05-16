from odoo import models, fields

class EstatePropertyTags(models.Model):
    _name = 'estate_property_tags'
    _description = 'Estate Managment Tags'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color')

    """ SQL Constraints """

    _sql_constraints = {
        ('unique_tag_name', 'UNIQUE(name)', 'Tag name must be unique!')
    }