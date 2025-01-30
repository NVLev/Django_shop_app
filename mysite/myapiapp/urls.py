from django.urls import path

from .views import GroupsListView, helo_world_view

app_name = "myapiapp"
urlpatterns = [
    path("hello/", helo_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
]
