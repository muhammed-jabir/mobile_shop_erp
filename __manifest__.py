{
    'name': 'Mobile Shop ERP',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Mobile Shop Sales, Inventory, Accounting and Service Management',
    'author': 'Jabir',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'contacts',
        'sale_management',
        'purchase',
        'stock',
        'account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/product_template_views.xml',
        'views/mobile_devices_views.xml',
        'reports/sale_reports.xml',
        'views/sale_views.xml',
        'views/expense_views.xml',
        'views/cash_flow_views.xml',
        'views/partner_views.xml',
        'views/dashboard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'web/static/lib/Chart/Chart.js',
            'mobile_shop_erp/static/src/js/dashboard.js',
            'mobile_shop_erp/static/src/xml/dashboard.xml',
        ],
    },

    'installable': True,
    'application': True,
}