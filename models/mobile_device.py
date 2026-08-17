from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MobileDevice(models.Model):
    _name = 'mobile.shop.device'
    _description = 'Mobile Device'
    _order = 'id desc'

    _sql_constraints = [
        ('imei_1_unique', 'unique(imei_1)', 'IMEI 1 already exists in the system.'),
        ('imei_2_unique', 'unique(imei_2)', 'IMEI 2 already exists in the system.'),
    ]

    name = fields.Char(
        string='Device Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )

    imei_1 = fields.Char(
        string='IMEI 1',
        required=True,
        copy=False,
    )

    imei_2 = fields.Char(
        string='IMEI 2',
        copy=False,
    )

    serial_number = fields.Char(
        string='Serial Number',
        copy=False,
    )

    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain="[('supplier_rank', '>', 0)]",
    )

    purchase_date = fields.Date(
        string='Purchase Date',
    )

    purchase_price = fields.Float(
        string='Purchase Price',
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain="[('customer_rank', '>', 0)]",
    )

    sale_date = fields.Date(
        string='Sale Date',
    )

    sale_price = fields.Float(
        string='Sale Price',
    )

    state = fields.Selection(
        [
            ('available', 'Available'),
            ('sold', 'Sold'),
            ('repair', 'Under Repair'),
            ('returned', 'Returned'),
        ],
        string='Status',
        default='available',
        required=True,
    )

    warranty_start = fields.Date(
        string='Warranty Start',
    )

    warranty_end = fields.Date(
        string='Warranty End',
    )

    notes = fields.Text(
        string='Notes',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'mobile.shop.device'
                ) or 'New'
        return super().create(vals_list)

    @api.constrains('imei_1', 'imei_2')
    def _check_imei_unique(self):
        for record in self:

            if record.imei_1 and record.imei_2 and record.imei_1 == record.imei_2:
                raise ValidationError(
                    'IMEI 1 and IMEI 2 cannot be identical.'
                )

            if record.imei_1:
                duplicate = self.search([
                    ('imei_1', '=', record.imei_1),
                    ('id', '!=', record.id),
                ], limit=1)

                if duplicate:
                    raise ValidationError(
                        'IMEI 1 already exists.'
                    )

            if record.imei_2:
                duplicate = self.search([
                    ('imei_2', '=', record.imei_2),
                    ('id', '!=', record.id),
                ], limit=1)

                if duplicate:
                    raise ValidationError(
                        'IMEI 2 already exists.'
                    )