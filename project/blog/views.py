from comments.forms import CommentForm
from comments.models import Comment
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from users.mixins import (
    IsAuthorDraftRequiredMixin,
    IsAuthorRequiredMixin,
    IsStaffRequiredMixin,
)

from .forms import AddPostForm, EditStaffPostForm
from .mixins import TitleMixin
from .models import Post

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
    template_name = "blog/unpublished_posts.html"
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
        """Add in context comment form object"""
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            context["form"] = self.comment_form()
        return context

    def post(self, request, *args, **kwargs):
        """Create post comment, if method is POST"""
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


class UnpublishedPostDetailView(IsStaffRequiredMixin, PostDetailView):
    """Unpublished post detail view"""

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

    def form_valid(self, form):
        """Add current user as author in post object"""
        self.instanse = form.save(commit=False)
        self.instanse.author = self.request.user
        self.instanse.save()
        return super().form_valid(form)


class EditUnpublishedPost(IsStaffRequiredMixin, TitleMixin, UpdateView):
    """View for staff to edit an unpublished post"""

    title = "Редактирование поста"
    model = Post
    form_class = EditStaffPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"
    success_url = reverse_lazy("home")


class EditDraftPost(IsAuthorDraftRequiredMixin, TitleMixin, UpdateView):
    """View for staff to edit a draft"""

    title = "Редактирование поста"
    model = Post
    form_class = AddPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"
    success_url = reverse_lazy("drafts")


def about(request):
    """Page about view"""
    return HttpResponse("about")


def gallery(request):
    """Page gallery view"""
    return HttpResponse("gallery")


def contact(request):
    """Page contact view"""
    return HttpResponse("contact")
