from csv import DictReader
from http.client import HTTPResponse
from io import TextIOWrapper

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .common import save_csv_products
from .forms import CSVImportForm
from .models import Order, Product, ProductImage


class OrderInline(admin.TabularInline):
    model = Product.orders.through
    extra = 0


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=False)


class OrderProductInline(admin.TabularInline):
    model = Order.products.through
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductImageInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = ["price", "name"]
    search_fields = ["name", "discount"]
    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price Options",
            {
                "fields": ("price", "discount"),
                "classes": ("collapse", "wide"),
            },
        ),
        (
            "Extra Options",
            {
                "fields": ("archived",),
                "classes": ("collapse", "wide"),
                "description": "Extra option, for disactivation",
            },
        ),
    ]

    @admin.display(description="Short description")
    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

    def import_csv(self, request: HttpRequest) -> HTTPResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        save_csv_products(file=form.files["csv_file"].file, encoding=request.encoding)
        # reader = DictReader(csv_file)
        # for row in reader:
        #     Product.objects.create(
        #         name=row['name'],
        #         description=row['description'],
        #         price=decimal.Decimal(row['price']),
        #         discount=int(row['discount']),
        #         created_by=request.user
        #     )

        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import_products_csv/", self.import_csv, name="import_products_csv")
        ]
        return new_urls + urls


# admin.site.register(Product, ProductAdmin)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProductInline,
    ]
    list_display = "pk", "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def import_csv(self, request: HttpRequest) -> HTTPResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        csv_file = TextIOWrapper(form.files["csv_file"].file, encoding=request.encoding)
        reader = DictReader(csv_file)
        for row in reader:
            order = Order.objects.create(
                delivery_address=row["delivery_address"],
                promocode=row["promocode"],
                user=request.user,
            )
            product_ids = [
                int(x.strip()) for x in row.get("product_ids", "").split(",") if x.strip()
            ]  # Handle missing or empty product_ids gracefully
            products = Product.objects.filter(pk__in=product_ids)
            order.products.set(products)
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path("import_orders_csv/", self.import_csv, name="import_orders_csv")]
        return new_urls + urls

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
