from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from comments.forms import CommentForm
from comments.models import Comment
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pinned_posts = self.model.objects.filter(is_pinned=True).select_related()
        if pinned_posts:
            context["pinned_posts"] = pinned_posts
        return context


class UnpublishedPostsView(IsStaffRequiredMixin, TitleMixin, ListView):
    title = "Неопубликованные посты"
    model = Post
    template_name = "blog/unpublished_posts.html"
    paginate_by = 5
    context_object_name = "posts"
    queryset = Post.objects.filter(is_draft=False).filter(is_published=False).order_by("-time_update").select_related()


class DraftPostsView(IsAuthorRequiredMixin, TitleMixin, ListView):
    title = "Черновики"
    model = Post
    template_name = "blog/unpublished_posts.html"
    paginate_by = 5
    context_object_name = "posts"

    def get_queryset(self):
        queryset = (
            Post.objects.filter(is_draft=True)
            .filter(author=self.request.user)
            .order_by("-time_create")
            .select_related()
        )
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/single_post.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"
    queryset = model.objects.filter(is_draft=False).filter(is_published=True).select_related()
    comment_form = CommentForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            context["form"] = self.comment_form()
        return context

    def post(self, request, *args, **kwargs):
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
        else:
            self.object = self.get_object()
            context = super().get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context=context)


class UnpublishedPostDetailView(IsStaffRequiredMixin, PostDetailView):
    model = Post
    queryset = model.objects.filter(is_draft=False).filter(is_published=False)


class DraftPostDetailView(IsAuthorDraftRequiredMixin, PostDetailView):
    model = Post
    queryset = model.objects.filter(is_draft=True).filter(is_published=False)


class AddPost(IsAuthorRequiredMixin, TitleMixin, CreateView):
    title = "Добавить пост"
    form_class = AddPostForm
    template_name = "blog/addpost.html"
    success_url = reverse_lazy("drafts")

    def form_valid(self, form):
        self.instanse = form.save(commit=False)
        self.instanse.author = self.request.user
        self.instanse.save()
        return super().form_valid(form)


class EditUnpublishedPost(IsStaffRequiredMixin, TitleMixin, UpdateView):
    title = "Редактирование поста"
    model = Post
    form_class = EditStaffPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"
    success_url = reverse_lazy("home")


class EditDraftPost(IsAuthorDraftRequiredMixin, TitleMixin, UpdateView):
    title = "Редактирование поста"
    model = Post
    form_class = AddPostForm
    template_name = "blog/edit_post.html"
    slug_url_kwarg = "post_slug"
    success_url = reverse_lazy("drafts")


def about(request):
    return HttpResponse("about")


def gallery(request):
    return HttpResponse("gallery")


def contact(request):
    return HttpResponse("contact")
