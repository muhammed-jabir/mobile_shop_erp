from odoo import models, fields
from datetime import timedelta


class MobileShopDashboard(models.AbstractModel):
    _name = 'mobile.shop.dashboard'
    _description = 'Mobile Shop Dashboard Data'

    def get_dashboard_data(self):
        today = fields.Date.context_today(self)

        sale_model = self.env['mobile.shop.sale']
        expense_model = self.env['mobile.shop.expense']
        device_model = self.env['mobile.shop.device']

        today_sales = sum(sale_model.search([
            ('sale_date', '=', today),
            ('state', '=', 'confirmed'),
        ]).mapped('sale_price'))

        today_expenses = sum(expense_model.search([
            ('date', '=', today),
        ]).mapped('amount'))

        stock_counts = {
            'available': device_model.search_count([('state', '=', 'available')]),
            'sold': device_model.search_count([('state', '=', 'sold')]),
            'repair': device_model.search_count([('state', '=', 'repair')]),
            'returned': device_model.search_count([('state', '=', 'returned')]),
        }

        trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_total = sum(sale_model.search([
                ('sale_date', '=', day),
                ('state', '=', 'confirmed'),
            ]).mapped('sale_price'))
            trend.append({
                'date': day.strftime('%d %b'),
                'total': day_total,
            })

        return {
            'today_sales': today_sales,
            'today_expenses': today_expenses,
            'stock_counts': stock_counts,
            'trend': trend,
        }