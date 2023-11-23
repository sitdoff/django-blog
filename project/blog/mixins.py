class TitleMixin:
    """Add title atribute in view"""

    title = ""

    def get_context_data(self, *, object_list=None, **kwargs):
        """Add title in context"""
        context = super().get_context_data(**kwargs)
        if self.title:
            context["title"] = self.title
        return context
