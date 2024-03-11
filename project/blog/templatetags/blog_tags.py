from django import template

register = template.Library()

navigation_menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "Подписки", "url_name": "subscriptions"},
    {"title": "Обо мне", "url_name": "about"},
    {"title": "Галлерея", "url_name": "gallery"},
    {"title": "Контакты", "url_name": "contact"},
]


@register.inclusion_tag("blog/tags_templates/navigation_menu.html")
def navigation(user):
    """Insert navigation menu in template"""
    return {"navigation_menu": navigation_menu, "user": user}


@register.inclusion_tag("blog/tags_templates/pagination.html")
def pagination(paginator, page_obj):
    """Inser pagination in template"""
    return {"page_obj": page_obj, "paginator": paginator}


@register.inclusion_tag("blog/tags_templates/author_buttons_for_drafts.html", takes_context=True)
def author_buttons_for_drafts(context):
    """
    Inserts buttons for reading or editing a draft on the Drafts page.
    """
    return {"post": context["post"]}


@register.inclusion_tag("blog/tags_templates/author_buttons_for_single_draft.html", takes_context=True)
def author_buttons_for_single_draft(context):
    """
    Inserts buttons for editing on the draft reading page.
    """
    return {"post": context["post"], "request": context["request"]}


@register.inclusion_tag("blog/tags_templates/staff_buttons_for_unpublished_posts.html", takes_context=True)
def staff_buttons_for_unpublished_posts_tag(context):
    """
    Inserts buttons to assign an editor or read a post.
    """
    return {"post": context["post"], "request": context["request"]}


@register.inclusion_tag("blog/tags_templates/staff_buttons_for_unpublished_single_post.html", takes_context=True)
def staff_buttons_for_unpublished_single_post_tag(context):
    """
    Inserts buttons to assign an editor or edit a post on the unpublished post page.
    """
    return {"post": context["post"], "request": context["request"]}


@register.inclusion_tag("blog/tags_templates/messages.html", takes_context=True)
def messages_tag(context):
    """
    Add container for messages
    """
    return {"messages": context["messages"]}
