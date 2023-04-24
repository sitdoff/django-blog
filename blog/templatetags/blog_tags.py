from django import template

register = template.Library()

navigation_menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "Обо мне", "url_name": "about"},
    {"title": "Галлерея", "url_name": "gallery"},
    {"title": "Контакты", "url_name": "contact"},
    {"title": "Добавить пост", "url_name": "add_post"},
]


@register.inclusion_tag("blog/navigation_menu.html")
def navigation(user):
    return {"navigation_menu": navigation_menu, "user": user}
