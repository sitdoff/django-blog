from django import template

register = template.Library()


@register.inclusion_tag("users/auth_menu.html")
def auth_menu(user) -> dict:
    """Return current user object for auth menu"""
    return {"user": user}


@register.inclusion_tag("users/author_info.html")
def author_info(author) -> dict:
    """Return author user object for author info"""
    return {"author": author}


@register.inclusion_tag("users/tags_templates/subscribe.html", takes_context=True)
def subscribe_link(context):
    """
    Adds a link to subscribe
    """
    return {"author": context["post"].author, "user": context["user"]}
