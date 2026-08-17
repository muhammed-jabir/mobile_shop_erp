from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shop_product_type = fields.Selection(
        [
            ('mobile_phone', 'Mobile Phone'),
            ('accessory', 'Accessory'),
            ('other', 'Other'),
        ],
        string='Shop Product Type',
        default='other',
    )

    shop_brand = fields.Char(
        string='Brand',
    )

    shop_model_name = fields.Char(
        string='Model',
    )

    shop_ram = fields.Char(
        string='RAM',
        help='e.g. 8GB',
    )

    shop_storage = fields.Char(
        string='Storage',
        help='e.g. 128GB',
    )

    shop_color = fields.Char(
        string='Color',
    )

    shop_warranty_period = fields.Integer(
        string='Warranty Period (Months)',
        default=0,
    )