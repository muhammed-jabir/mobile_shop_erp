from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MobileShopSaleLine(models.Model):
    _name = 'mobile.shop.sale.line'
    _description = 'Mobile Shop Sale Line'
    _order = 'id'

    sale_id = fields.Many2one(
        'mobile.shop.sale',
        string='Sale',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )

    device_id = fields.Many2one(
        'mobile.shop.device',
        string='Mobile Device',
        ondelete='restrict',
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )

    unit_price = fields.Monetary(
        string='Selling Price',
        required=True,
        currency_field='currency_id',
    )

    cost_price = fields.Monetary(
        string='Cost Price',
        currency_field='currency_id',
    )

    discount = fields.Float(
        string='Discount (%)',
        default=0.0,
    )

    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    profit = fields.Monetary(
        string='Profit',
        compute='_compute_profit',
        store=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        related='sale_id.currency_id',
        store=True,
        readonly=True,
    )

    @api.depends('quantity', 'unit_price', 'discount')
    def _compute_subtotal(self):
        for line in self:
            price = line.unit_price * line.quantity
            discount_amount = price * (line.discount / 100.0)
            line.subtotal = price - discount_amount

    @api.depends('quantity', 'unit_price', 'cost_price', 'discount')
    def _compute_profit(self):
        for line in self:
            selling_amount = line.unit_price * line.quantity
            discount_amount = selling_amount * (line.discount / 100.0)
            selling_amount -= discount_amount

            cost_amount = line.cost_price * line.quantity

            line.profit = selling_amount - cost_amount

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    'Quantity must be greater than zero.'
                )

    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if line.discount < 0 or line.discount > 100:
                raise ValidationError(
                    'Discount must be between 0 and 100%.'
                )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.unit_price = line.product_id.lst_price