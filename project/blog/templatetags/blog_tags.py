from django import template

register = template.Library()

navigation_menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "Обо мне", "url_name": "about"},
    {"title": "Галлерея", "url_name": "gallery"},
    {"title": "Контакты", "url_name": "contact"},
]


@register.inclusion_tag("blog/navigation_menu.html")
def navigation(user):
    """Insert navigation menu in template"""
    return {"navigation_menu": navigation_menu, "user": user}


@register.inclusion_tag("blog/pagination.html")
def pagination(paginator, page_obj):
    """Inser pagination in template"""
    return {"page_obj": page_obj, "paginator": paginator}
