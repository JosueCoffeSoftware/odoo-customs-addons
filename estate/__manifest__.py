# -*- coding: utf-8 -*-

{
    'name': 'Estate Management',
    'depends': ['base'],
    'application': True,
    'license':'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menu.xml',
    ],
}