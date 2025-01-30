from django.urls import include, path

from .views import ArticleDetailView, ArticleListView

app_name = "blogapp"

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles_list"),
    path("articles/<int:pk>", ArticleDetailView.as_view(), name="article"),
]
