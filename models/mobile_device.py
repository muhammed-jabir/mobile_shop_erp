from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MobileDevice(models.Model):
    _name = 'mobile.shop.device'
    _description = 'Mobile Device'
    _order = 'id desc'

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

    @api.constrains('imei_1', 'imei_2')
    def _check_imei_unique(self):
        for record in self:

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