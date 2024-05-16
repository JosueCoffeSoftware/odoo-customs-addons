from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate_property_offer'
    _description = 'Estate Managment Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price', required=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], string='Status', default='accepted', required=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate_property', string='Property', required=True)
    validity = fields.Integer(string='Validity(Days)', default=7)
    date_deadline = fields.Date(string='Deadline Date', compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    create_date = fields.Datetime(string='Creation Date', default=lambda self: fields.Datetime.now())
    property_type_id = fields.Many2one('estate_property_type', string="Property Type", related="property_id.property_type_id", store=True)

    """ Depends && Functions or Methods """

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.validity:
                create_date = fields.Datetime.from_string(offer.create_date)
                offer.date_deadline = (create_date + timedelta(days=offer.validity)).date()

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                create_date = fields.Datetime.from_string(offer.create_date)
                deadline_date = fields.Date.from_string(offer.date_deadline)
                offer.validity = (deadline_date - create_date.date()).days

    def action_accept(self):
        for offer in self:
            if offer.property_id.state != 'new' and offer.property_id.state != 'offer_received':
                raise exceptions.UserError("Cannot accept an offer for a property that is not available.")
            offer.property_id.state = 'offer_accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price

    def action_refused(self):
        for offer in self:
            if offer.property_id != 'new' and offer.property_id.state != 'offer_received':
                raise exceptions.UserError("Cannot refuse an offer for a propert that is not available")
            offer.property_id.state = 'new'
    
    @api.constrains('price')
    def _check_offer_price_positive(self):
        for offer in self:
            if offer.price <= 0:
                raise exceptions.ValidationError('Offer price must be strictly positive!')
    
    @api.model
    def create(self, vals):
        if 'price' in vals:
            existing_offers = self.search([('property_id', '=', vals.get('property_id', False))])
            if existing_offers and any(existing_offer.price <= vals['price'] for existing_offer in existing_offers):
                raise exceptions.UserError("You cannot create an offer with a lower price than an existing offer.")
        property_obj = self.env['estate_property'].browse(vals.get('property_id'))
        if property_obj:
            property_obj.state = 'offer_received'
        return super(EstatePropertyOffer, self).create(vals)
            
    """ SQL Constraints """

    _sql_constraints = {
        ('check_offer_price_positive', 'CHECK(price > 0)', 'Offer price must be strictly positive!')
    }