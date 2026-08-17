from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MobileShopSale(models.Model):
    _name = 'mobile.shop.sale'
    _description = 'Mobile Shop Sale / Billing'
    _order = 'id desc'

    # ============================================================
    # BASIC INFORMATION
    # ============================================================

    name = fields.Char(
        string='Bill Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain="[('customer_rank', '>', 0)]",
    )

    sale_date = fields.Date(
        string='Sale Date',
        required=True,
        default=fields.Date.context_today,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # ============================================================
    # SALE LINES
    # ============================================================

    line_ids = fields.One2many(
        'mobile.shop.sale.line',
        'sale_id',
        string='Sale Items',
        copy=True,
    )

    payment_ids = fields.One2many(
        'mobile.shop.payment',
        'sale_id',
        string='Payments',
        copy=False,
    )

    # ============================================================
    # TOTALS
    # ============================================================

    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    discount_amount = fields.Monetary(
        string='Discount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    total_amount = fields.Monetary(
        string='Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    total_profit = fields.Monetary(
        string='Total Profit',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ============================================================
    # PAYMENT / BALANCE
    # ============================================================

    amount_paid = fields.Monetary(
        string='Amount Paid',
        compute='_compute_payment_status',
        store=True,
        currency_field='currency_id',
    )

    amount_due = fields.Monetary(
        string='Amount Due',
        compute='_compute_payment_status',
        store=True,
        currency_field='currency_id',
    )

    payment_status = fields.Selection(
        [
            ('unpaid', 'Unpaid'),
            ('partial', 'Partially Paid'),
            ('paid', 'Paid'),
        ],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True,
        default='unpaid',
    )

    # ============================================================
    # STATUS
    # ============================================================

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
    )

    notes = fields.Text(
        string='Notes',
    )

    # ============================================================
    # CREATE
    # ============================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'mobile.shop.sale'
                    )
                    or 'New'
                )

        return super().create(vals_list)

    # ============================================================
    # TOTAL CALCULATION
    # ============================================================

    @api.depends(
        'line_ids.subtotal',
        'line_ids.unit_price',
        'line_ids.quantity',
        'line_ids.discount',
        'line_ids.cost_price',
    )
    def _compute_totals(self):
        for sale in self:
            subtotal = 0.0
            total_cost = 0.0

            for line in sale.line_ids:
                subtotal += (
                    line.unit_price * line.quantity
                )

                total_cost += (
                    line.cost_price * line.quantity
                )

            total_amount = sum(
                line.subtotal
                for line in sale.line_ids
            )

            discount_amount = subtotal - total_amount

            sale.subtotal = subtotal
            sale.discount_amount = discount_amount
            sale.total_amount = total_amount
            sale.total_cost = total_cost
            sale.total_profit = total_amount - total_cost

    # ============================================================
    # PAYMENT STATUS
    # ============================================================

    @api.depends(
        'payment_ids.amount',
        'payment_ids.state',
        'total_amount',
    )
    def _compute_payment_status(self):
        for sale in self:

            confirmed_payments = sale.payment_ids.filtered(
                lambda payment: payment.state == 'confirmed'
            )

            amount_paid = sum(
                confirmed_payments.mapped('amount')
            )

            due = sale.total_amount - amount_paid

            if due < 0:
                due = 0.0

            sale.amount_paid = amount_paid
            sale.amount_due = due

            if amount_paid <= 0:
                sale.payment_status = 'unpaid'

            elif amount_paid < sale.total_amount:
                sale.payment_status = 'partial'

            else:
                sale.payment_status = 'paid'

    # ============================================================
    # CONFIRM SALE
    # ============================================================

    def action_confirm(self):
        for sale in self:

            if sale.state == 'confirmed':
                raise ValidationError(
                    'This bill is already confirmed.'
                )

            if not sale.line_ids:
                raise ValidationError(
                    'You must add at least one item before confirming the sale.'
                )

            total_payments = sum(
                sale.payment_ids.mapped('amount')
            )

            if total_payments > sale.total_amount:
                raise ValidationError(
                    'Total payments cannot be greater than the sale total.'
                )

            for line in sale.line_ids:

                # ------------------------------------------------
                # Device validation
                # ------------------------------------------------

                if line.device_id:

                    device = line.device_id

                    if device.state != 'available':
                        raise ValidationError(
                            f'Device {device.name} is not available for sale.'
                        )

                    if device.product_id != line.product_id:
                        raise ValidationError(
                            'The selected device does not belong to '
                            'the selected product.'
                        )

                    # ------------------------------------------------
                    # Mark device as sold
                    # ------------------------------------------------

                    device.write({
                        'state': 'sold',
                        'customer_id': sale.customer_id.id,
                        'sale_date': sale.sale_date,
                        'sale_price': line.unit_price,
                    })

            sale.state = 'confirmed'

            sale.payment_ids.write({
                'state': 'confirmed'
            })

    # ============================================================
    # VIEW CUSTOMER
    # ============================================================

    def action_view_customer(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.customer_id.id,
        }

    # ============================================================
    # VIEW DEVICES
    # ============================================================

    def action_view_devices(self):
        self.ensure_one()

        device_ids = self.line_ids.mapped(
            'device_id'
        ).ids

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sold Devices',
            'res_model': 'mobile.shop.device',
            'view_mode': 'tree,form',
            'domain': [
                ('id', 'in', device_ids)
            ],
        }