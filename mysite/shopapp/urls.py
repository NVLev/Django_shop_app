from django.db import router
from django.urls import include, path
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (
    GroupsListView,
    LatestProductsFeed,
    OrderCreateView,
    OrderDataExportView,
    OrderDeleteView,
    OrderDetailView,
    OrdersListView,
    OrderUpdateView,
    OrderViewSet,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailsView,
    ProductsListView,
    ProductUpdateView,
    ProductViewSet,
    ShopIndexView,
    UserOrderExportView,
    UserOrdersListView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)


urlpatterns = [
    path("", cache_page(60 * 2)(ShopIndexView.as_view()), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create", ProductCreateView.as_view(), name="product_form"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product-details"),
    path(
        "products/<int:pk>/archive",
        ProductDeleteView.as_view(),
        name="product_confirm_delete",
    ),
    path("products/latest/feed", LatestProductsFeed(), name="product-feed"),
    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name="order_update_form"),
    path(
        "orders/<int:pk>/delete", OrderDeleteView.as_view(), name="order_confirm_delete"
    ),
    path("orders/create", OrderCreateView.as_view(), name="order_form"),
    path("orders/export", OrderDataExportView.as_view(), name="order_export"),
    path(
        "users/<int:user_id>/orders/",
        UserOrdersListView.as_view(),
        name="user_order_list",
    ),
    path(
        "users/<int:user_id>/orders/export/",
        UserOrderExportView.as_view(),
        name="user_order_export",
    ),
]
