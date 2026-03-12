{
    "name": "Library Management",
    "version": "1.0",
    "summary": "Manage Books and Members etc.",
    "description": """It is a standard library management module, to manage
    Books, members which helps the improvement of library management""",
    "author": "Rudra",
    "category": "Education",
    "depends": ['base', 'mail'],
    "data": [
        "security/library_management_security.xml",
        "security/ir.model.access.csv",
        "views/book.xml",
        "views/category.xml",
        "views/borrow.xml",
        "views/member.xml",
        "views/menu.xml",
        "data/cron.xml",
    ],
    "demo": [
        "data/library_management_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}