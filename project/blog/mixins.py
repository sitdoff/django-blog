class TitleMixin:
    title = ""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.title:
            context["title"] = self.title
        return context
