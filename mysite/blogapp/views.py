from blogapp.models import Article
from django.shortcuts import render
from django.views.generic import DetailView, ListView


class ArticleListView(ListView):
    template_name = "blogapp/templates/blogapp/article_list"
    context_object_name = "article"
    queryset = (
        Article.objects.select_related("author", "category")
        .prefetch_related("tags")
        .defer("content")
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")
    )


class ArticleDetailView(DetailView):
    model = Article
