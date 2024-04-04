from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.db.models import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from comments.forms import CommentForm
from users.mixins import (
    IsAuthorDraftRequiredMixin,
    IsAuthorRequiredMixin,
    IsStaffRequiredMixin,
)

from .forms import AddPostForm, EditStaffPostForm, FeedbackForm, SearchForm
from .mixins import TitleMixin
from .models import Post
from .redis_services import increase_post_views
from .tasks import send_feedback_task

# Create your views here.


class IndexView(TitleMixin, ListView):
    """Main page view"""

    title = "Главная страница"
    model = Post
    template_name = "blog/index.html"
    paginate_by = 5
    context_object_name = "posts"
    queryset = (
        Post.objects.filter(is_draft=False)
        .filter(is_published=True)
        .filter(is_pinned=False)
        .order_by("-time_update")
        .select_related()
    )

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """Add in context pinned post object"""
        context = super().get_context_data(**kwargs)
        if pinned_posts := self.model.objects.filter(is_pinned=True).select_related():
            context["pinned_posts"] = pinned_posts
        return context


class SubscriptionsView(LoginRequiredMixin, TitleMixin, ListView):
    """
    Subscriptions view
    """

    title = "Мои подписки"
    model = Post
    template_name = "blog/subscriptions_posts.html"
    paginate_by = 5
    context_object_name = "posts"
    login_url = reverse_lazy("users:login")

    def get_queryset(self):
        """
        Returns posts only from those authors who are in the current user's subscriptions.
        """
        queryset = self.model.objects.filter(
            author__username__in=self.request.session["subscriptions"],
            is_published=True,
        ).select_related()
        return queryset


class UnpublishedPostsView(IsStaffRequiredMixin, TitleMixin, ListView):
    """Unpublished Posts View"""

    title = "Неопубликованные посты"
    model = Post
    template_name = "blog/unpublished_posts.html"
    paginate_by = 5
    context_object_name = "posts"
    queryset = Post.objects.filter(is_draft=False).filter(is_published=False).order_by("-time_update").select_related()


class DraftPostsView(IsAuthorRequiredMixin, TitleMixin, ListView):
    """Drafts view"""

    title = "Черновики"
    model = Post
    template_name = "blog/draft_posts.html"
    paginate_by = 5
    context_object_name = "posts"

    def get_queryset(self):
        """Return queryset with drafts"""
        queryset = (
            Post.objects.filter(is_draft=True)
            .filter(author=self.request.user)
            .order_by("-time_create")
            .select_related()
        )
        return queryset


class PostDetailView(DetailView):
    """Post detail view"""

    model = Post
    template_name = "blog/single_post.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"
    queryset = model.objects.filter(is_draft=False).filter(is_published=True).select_related()
    comment_form = CommentForm

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Add in context comment form object
        """
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            context["form"] = self.comment_form()
        return context

    def post(self, request, *args, **kwargs):
        """
        Create post comment, if method is POST
        """
        post = get_object_or_404(self.model, slug=kwargs["post_slug"])
        author = request.user
        content = request.POST["content"]
        form = CommentForm({"post": post, "author": author, "content": content})
        if form.is_valid():
            form.save()
            self.object = self.get_object()
            context = super().get_context_data(**kwargs)
            context["form"] = self.comment_form()
            return self.render_to_response(context=context)
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context=context)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Increases the number of views if there are no cookies. Sets the cookie if it does not exist.
        """
        response: HttpResponse = super().get(request, *args, **kwargs)
        object_instance = self.get_object()
        cookie_name = "post_view_" + str(object_instance.pk)
        if cookie_name not in self.request.COOKIES:
            increase_post_views(object_instance)
            response.set_cookie(cookie_name, "true", max_age=3600 * 24 * 30 * 12)

        return response


class UnpublishedPostDetailView(IsStaffRequiredMixin, PostDetailView):
    """
    Unpublished post detail view
    """

    model = Post
    queryset = model.objects.filter(is_draft=False).filter(is_published=False)


class DraftPostDetailView(IsAuthorDraftRequiredMixin, PostDetailView):
    """Draft detail view"""

    model = Post
    queryset = model.objects.filter(is_draft=True).filter(is_published=False)


class AddPost(IsAuthorRequiredMixin, TitleMixin, CreateView):
    """View for authors to create a post"""

    title = "Добавить пост"
    form_class = AddPostForm
    template_name = "blog/addpost.html"
    success_url = reverse_lazy("drafts")

    def get_form_kwargs(self):
        """
        Add a request to the form attributes.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class EditUnpublishedPost(IsStaffRequiredMixin, TitleMixin, UpdateView):
    """View for staff to edit an unpublished post"""

    title = "Редактирование поста"
    model = Post
    form_class = EditStaffPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"

    def get_success_url(self):
        """
        Return a redirect to view the post being edited, if available,
        otherwise returns a redirect to the list of unpublished posts.
        """
        if self.object.is_draft or self.object.is_published:
            return reverse("unpublished_posts")
        return reverse("unpublished_post", kwargs={"post_slug": self.object.slug})

    def get_form_kwargs(self):
        """
        Add a request to the form attributes.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self):
        """
        Return a queryset with posts that are not draft or published.
        """

        queryset = self.model.objects.filter(is_draft=False).filter(is_published=False).select_related()
        return queryset


class EditDraftPost(IsAuthorDraftRequiredMixin, TitleMixin, UpdateView):
    """View for staff to edit a draft"""

    title = "Редактирование поста"
    model = Post
    form_class = AddPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"
    success_url = reverse_lazy("drafts")

    def get_queryset(self):
        """
        Returns a queryset with posts that are drafts and owned by the current user.

        The superuser can see all drafts.
        """
        if self.request.user.is_superuser:
            queryset = Post.objects.filter(is_draft=True).select_related()
            return queryset
        queryset = Post.objects.filter(is_draft=True).filter(author=self.request.user).select_related()
        return queryset

    def get_form_kwargs(self):
        """
        Add a request to the form attributes.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@user_passes_test(lambda user: user.is_staff, login_url=reverse_lazy("users:login"))
@require_POST
def set_editor(request: HttpRequest) -> HttpResponseRedirect:
    """
    Sets the editor for the post.
    """
    post: Post = get_object_or_404(Post, slug=request.POST["post_slug"])
    if not post.editor and not post.is_published:
        post.editor = request.user
        post.save()
        messages.add_message(request, messages.SUCCESS, "Вы взяли пост на редактирование.")
        return HttpResponseRedirect(reverse_lazy("unpublished_post", kwargs={"post_slug": post.slug}))
    messages.add_message(request, messages.ERROR, "У поста уже есть редактор.")
    return HttpResponseRedirect(reverse_lazy("unpublished_posts"))


def about(request):
    """
    Page about view
    """
    return TemplateResponse(request, "blog/about.html")


def gallery(request):
    """
    Page gallery view
    """
    return TemplateResponse(request, "blog/gallery.html")


def contact(request: HttpRequest) -> HttpResponse:
    """
    Page contact view
    """
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            send_feedback_task.delay(form.cleaned_data)
            return TemplateResponse(request, "blog/feedback_done.html")
    else:
        form = FeedbackForm()
    return render(request, "blog/contact.html", context={"form": form})


def search(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            posts = Post.objects.annotate(search=SearchVector("title", "article")).filter(
                search=request.GET["text"], is_published=True, is_draft=False
            )
            return render(request, "blog/search.html", context={"form": form, "posts": posts})
    form = SearchForm()
    return render(request, "blog/search.html", context={"form": form})
