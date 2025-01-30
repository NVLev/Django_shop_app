"""Набор представлений о товарах и заказах."""

import logging
from csv import DictWriter
from timeit import default_timer

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import Group
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_filters.rest_framework import DjangoFilterBackend
from jsonschema.cli import parser
from rest_framework.decorators import action, parser_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products
from .forms import GroupForm, ProductForm
from .models import Order, Product, ProductImage
from .serializers import OrderSerializer, ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    """

    Набор представлений для действий с  Product.
    Поллный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "description", "price", "discount", "archived"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "discount"]

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})
        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
            user=request.user,  # Pass the current user
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.select_related("user").prefetch_related("products")

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user",
        "products",
    ]
    search_fields = ["delivery_address", "products"]
    ordering_fields = ["user", "delivery_address", "created_at"]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:

        products = [
            ("T-shirts", 1000),
            ("Cups", 250),
            ("Calendars", 300),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        logger.debug("Products for shop index: %s", products)
        logger.info("Rendering shop index")
        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups_list.html", context=context)

    # происходит обработка формы
    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"

    def test_func(self):

        product = self.get_object()

        if self.request.user.is_superuser:
            return True

        if product.created_by == self.request.user:
            return True

        if self.request.user.has_perm("shopapp.change_product"):
            return True

        return False

    def handle_no_permission(self):
        raise PermissionDenied("You don't have permission to edit this product.")

    def get_success_url(self):
        return reverse(
            "shopapp:product-details",
            kwargs={"pk": self.object.pk},
        )


class ProductsListView(ListView):
    template_name = "shopapp/products_list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Product updates"
    link = reverse_lazy("shopapp:product-details")

    def items(self):
        return Product.objects.all.order_by("-article_date")[:10]

    def item_title(self, item):
        return item.name


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied("You don't have permission to access this page.")

    def get(self, request: HttpRequest) -> JsonResponse:
        orders: QuerySet[Order] = (
            Order.objects.select_related("user")
            .prefetch_related("products")
            .order_by("pk")
        )

        order_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.first_name or order.user.username,
                "products": [
                    {"name": product.name, "price": product.price}
                    for product in order.products.all()
                ],
            }
            for order in orders
        ]
        return JsonResponse({"orders": order_data})


class OrderUpdateView(UpdateView):
    model = Order
    fields = ["user", "delivery_address", "promocode", "products"]
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_detail",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class OrderCreateView(CreateView):
    model = Order
    fields = ["user", "delivery_address", "promocode", "products"]
    success_url = reverse_lazy("shopapp:order_list")


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_order_list.html"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        self.owner = get_object_or_404(get_user_model(), pk=user_id)
        return Order.objects.filter(user=self.owner).prefetch_related("products")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        context["owner_id"] = self.owner.id
        return context


class UserOrderExportView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(get_user_model(), pk=user_id)

        cache_key = f"user_orders_export_{user_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data, safe=False)

        orders = Order.objects.filter(user=user).order_by("pk")
        serializer = OrderSerializer(orders, many=True)
        data = serializer.data

        cache.set(cache_key, data, timeout=300)

        return JsonResponse(data, safe=False)
