{
    'name': 'Purchase Order Approval Hierarchy',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Implement level-by-level approval hierarchy and creator-only edit access for POs',
    'description': """    """,
    'author': 'Your Name',
    'depends': [
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}