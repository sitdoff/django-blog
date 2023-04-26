from django import template

register = template.Library()


@register.inclusion_tag("users/auth_menu.html")
def auth_menu(user):
    return {"user": user}
