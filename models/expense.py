from odoo import models, fields


class MobileShopExpense(models.Model):
    _name = 'mobile.shop.expense'
    _description = 'Mobile Shop Expense'
    _order = 'date desc'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )

    description = fields.Char(
        string='Description',
        required=True,
    )

    amount = fields.Float(
        string='Amount',
        required=True,
    )

    payment_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('upi', 'UPI'),
            ('bank', 'Bank Transfer'),
            ('card', 'Card'),
        ],
        string='Payment Method',
        required=True,
        default='cash',
    )