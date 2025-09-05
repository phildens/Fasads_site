from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Article



class ArticleListView(ListView):
    template_name = "articles/list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED)

class ArticleDetailView(DetailView):
    template_name = "articles/detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["more_articles"] = (
            Article.objects.filter(status=Article.Status.PUBLISHED)
            .exclude(pk=self.object.pk)
            .order_by("-published_at")[:20]
        )
        return ctx
