from app import Menu, Login, DishEdit, Template, Logout, Order

index = Menu.main

WSGI = {
    'Login': Login.main,
    'Logout': Logout.main,
    'Menu': Menu.main,
    'DishEdit': DishEdit.main,
    'Order': Order.main
}

AJAX = {
    'Menu': Menu.ajax,
    'Login': Login.ajax,
    'DishEdit': DishEdit.ajax,
    'Logout': Logout.ajax,
    'Order': Order.ajax
}

RESOURCE = {
    'Template': Template.res,
    'Menu': Menu.res,
    'Login': Login.res,
    'DishEdit': DishEdit.res,
    'Order': Order.res
}

APIs = {
    'ajax': AJAX,
    'res': RESOURCE
}
