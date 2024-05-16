from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class estate_property(models.Model):
    _name = 'estate_property'
    _description = 'Estate Management Property'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    postal_code = fields.Char(string='Postal Code')
    availability_date = fields.Date(string='Date Availability', copy=False, default=lambda self: (datetime.today() + timedelta(days=90)).date())
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False, required=True)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Garden Orientation')
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], string="State", default='new', required=True, copy=False)
    property_type_id = fields.Many2one('estate_property_type', string='Property Type', store=True)
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    seller_id = fields.Many2one('res.users', string='Seller', default=lambda self: self.env.user.id, copy=False)
    tag_ids = fields.Many2many('estate_property_tags', string='Tags')
    offer_ids = fields.One2many('estate_property_offer', 'property_id', string='Offers')
    total_area = fields.Integer(string='Total Area', compute='_compute_total_area')
    best_price = fields.Float(string='Best Price', compute='_compute_best_price')

    """ Depends && Functions or Methods """

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_cancel(self):
        for property in self:
            if property.state == 'sold':
                raise exceptions.UserError("Cannot cancel a property that is already sold.")
            property.state = "cancelled"

    def action_sold(self):
        for property in self:
            if property.state == 'cancelled':
                raise exceptions.UserError("Cannot mark a cancelled property as sold.")
            property.state == 'sold'

    @api.constrains('expected_price')
    def _check_expected_price_positive(self):
        for property in self:
            if property.expected_price <= 0:
                raise exceptions.ValidationError('Expected price must be strictly positive!')
            
    @api.constrains('selling_price')
    def check_selling_price_positive(self):
        for property in self:
            if property.selling_price < 0:
                raise exceptions.ValidationError('Selling price must be positive!')
            
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for property in self:
            if property.expected_price and property.selling_price < 0.9 * property.expected_price:
                raise exceptions.ValidationError('The sale price cannot be less than 90 percent of the expected price!')
    
    @api.ondelete(at_uninstall=False)
    def _check_property_deletion(self):
        for property in self:
            if property.state not in ['new', 'cancelled']:
                raise exceptions.UserError("You cannot delete a property that is not in 'New' or 'Cancelled' state")
    
    """ SQL Constraints """

    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive!'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'Selling price must be positive!')
    ]