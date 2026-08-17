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
        'views/mobile_devices_views.xml',
        'views/product_template_views.xml',
    ],

    'installable': True,
    'application': True,
}