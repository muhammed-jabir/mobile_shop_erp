from odoo import models, fields, api
from datetime import datetime, time


class MobileShopCashFlow(models.Model):
    _name = 'mobile.shop.cash.flow'
    _description = 'Daily Cash Flow'
    _order = 'date desc'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )

    opening_balance = fields.Float(
        string='Opening Balance',
    )

    sales_cash = fields.Float(
        string='Sales (Cash)',
        compute='_compute_sales_by_method',
    )
    sales_upi = fields.Float(
        string='Sales (UPI)',
        compute='_compute_sales_by_method',
    )
    sales_bank = fields.Float(
        string='Sales (Bank)',
        compute='_compute_sales_by_method',
    )
    sales_card = fields.Float(
        string='Sales (Card)',
        compute='_compute_sales_by_method',
    )
    sales_credit = fields.Float(
        string='Sales (Credit)',
        compute='_compute_sales_by_method',
    )

    total_sales = fields.Float(
        string='Total Sales',
        compute='_compute_sales_by_method',
    )

    expense_cash = fields.Float(
        string='Expenses (Cash)',
        compute='_compute_expenses_by_method',
    )
    expense_upi = fields.Float(
        string='Expenses (UPI)',
        compute='_compute_expenses_by_method',
    )
    expense_bank = fields.Float(
        string='Expenses (Bank)',
        compute='_compute_expenses_by_method',
    )
    expense_card = fields.Float(
        string='Expenses (Card)',
        compute='_compute_expenses_by_method',
    )

    total_expenses = fields.Float(
        string='Total Expenses',
        compute='_compute_expenses_by_method',
    )

    closing_balance = fields.Float(
        string='Closing Balance (Cash Only)',
        compute='_compute_closing_balance',
    )

    @api.depends('date')
    def _compute_sales_by_method(self):
        for record in self:
            if not record.date:
                record.sales_cash = record.sales_upi = record.sales_bank = 0.0
                record.sales_card = record.sales_credit = record.total_sales = 0.0
                continue

            day_start = datetime.combine(record.date, time.min)
            day_end = datetime.combine(record.date, time.max)

            payments = self.env['mobile.shop.payment'].search([
                ('payment_date', '>=', day_start),
                ('payment_date', '<=', day_end),
                ('state', '=', 'confirmed'),
            ])
            record.sales_cash = sum(payments.filtered(lambda p: p.payment_method == 'cash').mapped('amount'))
            record.sales_upi = sum(payments.filtered(lambda p: p.payment_method == 'upi').mapped('amount'))
            record.sales_bank = sum(payments.filtered(lambda p: p.payment_method == 'bank').mapped('amount'))
            record.sales_card = sum(payments.filtered(lambda p: p.payment_method == 'card').mapped('amount'))
            record.sales_credit = sum(payments.filtered(lambda p: p.payment_method == 'credit').mapped('amount'))
            record.total_sales = sum(payments.mapped('amount'))

    @api.depends('date')
    def _compute_expenses_by_method(self):
        for record in self:
            expenses = self.env['mobile.shop.expense'].search([
                ('date', '=', record.date),
            ])
            record.expense_cash = sum(expenses.filtered(lambda e: e.payment_method == 'cash').mapped('amount'))
            record.expense_upi = sum(expenses.filtered(lambda e: e.payment_method == 'upi').mapped('amount'))
            record.expense_bank = sum(expenses.filtered(lambda e: e.payment_method == 'bank').mapped('amount'))
            record.expense_card = sum(expenses.filtered(lambda e: e.payment_method == 'card').mapped('amount'))
            record.total_expenses = sum(expenses.mapped('amount'))

    @api.depends('opening_balance', 'sales_cash', 'expense_cash')
    def _compute_closing_balance(self):
        for record in self:
            record.closing_balance = (
                record.opening_balance + record.sales_cash - record.expense_cash
            )