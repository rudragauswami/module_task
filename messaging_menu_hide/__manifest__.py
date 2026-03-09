{
    'name': 'Hide Message Menu Icon',
    'version': '1.0',
    'depends': ['base', 'mail', 'web'],
    'assets': {
        'web.assets_backend': [
            'messaging_menu_hide/static/src/xml/hide_messaging_menu.xml',
        ],
    },
    'installable': True,
}