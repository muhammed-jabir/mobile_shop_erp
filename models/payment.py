from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MobileShopPayment(models.Model):
    _name = 'mobile.shop.payment'
    _description = 'Mobile Shop Payment'
    _order = 'payment_date desc, id desc'

    name = fields.Char(
        string='Payment Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    sale_id = fields.Many2one(
        'mobile.shop.sale',
        string='Sale',
        required=True,
        ondelete='cascade',
    )

    customer_id = fields.Many2one(
        related='sale_id.customer_id',
        string='Customer',
        store=True,
        readonly=True,
    )

    payment_date = fields.Datetime(
        string='Payment Date',
        required=True,
        default=fields.Datetime.now,
    )

    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        related='sale_id.currency_id',
        store=True,
        readonly=True,
    )

    payment_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('upi', 'UPI'),
            ('bank', 'Bank Transfer'),
            ('card', 'Card'),
            ('credit', 'Credit'),
        ],
        string='Payment Method',
        required=True,
        default='cash',
    )

    reference = fields.Char(
        string='Transaction Reference',
        help='UPI transaction ID, bank reference, card reference, etc.',
    )

    notes = fields.Text(
        string='Notes',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'mobile.shop.payment'
                    )
                    or 'New'
                )

        return super().create(vals_list)

    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(
                    'Payment amount must be greater than zero.'
                )

    def action_confirm(self):
        for payment in self:

            if payment.state == 'confirmed':
                continue

            if payment.sale_id.state != 'confirmed':
                raise ValidationError(
                    'You can only confirm a payment for a confirmed sale.'
                )

            payment.state = 'confirmed'