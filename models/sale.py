from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MobileShopSale(models.Model):
    _name = 'mobile.shop.sale'
    _description = 'Mobile Shop Sale / Billing'
    _order = 'id desc'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

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
    )

    device_id = fields.Many2one(
        'mobile.shop.device',
        string='Device',
        required=True,
        domain="[('state', '=', 'available')]",
    )

    product_id = fields.Many2one(
        related='device_id.product_id',
        string='Product',
        store=True,
        readonly=True,
    )

    sale_price = fields.Float(
        string='Sale Price',
        required=True,
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

    sale_date = fields.Date(
        string='Sale Date',
        required=True,
        default=fields.Date.context_today,
    )

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



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'mobile.shop.sale'
                ) or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for record in self:
            if record.state == 'confirmed':
                raise ValidationError('This bill is already confirmed.')

            if record.device_id.state != 'available':
                raise ValidationError(
                    'This device is not available for sale.'
                )

            record.device_id.write({
                'state': 'sold',
                'customer_id': record.customer_id.id,
                'sale_date': record.sale_date,
                'sale_price': record.sale_price,
            })

            record.state = 'confirmed'

    def action_view_device(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Device',
            'res_model': 'mobile.shop.device',
            'view_mode': 'form',
            'res_id': self.device_id.id,
        }