from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mobile_shop_sale_count = fields.Integer(
        string='Purchase Count',
        compute='_compute_mobile_shop_sale_count',
    )

    @api.depends('name')
    def _compute_mobile_shop_sale_count(self):
        for partner in self:
            partner.mobile_shop_sale_count = self.env['mobile.shop.sale'].search_count([
                ('customer_id', '=', partner.id),
                ('state', '=', 'confirmed'),
            ])

    def action_view_mobile_shop_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchases',
            'res_model': 'mobile.shop.sale',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id), ('state', '=', 'confirmed')],
        }