from itertools import count
from tkinter.constants import CASCADE

from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в интернет-магазине

    Заказы тут:   :model:`shopapp.Order`
    """

    class Meta:
        ordering = ["-name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Enter product name"),
        db_index=True,
    )

    description = models.TextField(
        null=False,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Product description"),
        db_index=True,
    )

    price = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Price"),
        help_text=_("Product price in USD"),
    )

    discount = models.SmallIntegerField(
        default=0, verbose_name=_("Discount"), help_text=_("Discount percentage")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    archived = models.BooleanField(
        default=False, verbose_name=_("Archived"), help_text=_("Is product archived?")
    )

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Created by")
    )

    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path,
        verbose_name=_("Preview image"),
        help_text=_("Product preview image"),
    )

    def __str__(self):
        return self.name

    def get_products_count(self, count):
        return ngettext("One product", "%(count) products", count) % {"count": count}

    def get_absolute_url(self):
        return reverse("shopapp:product-details", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"Product(pk={self.pk}, name={self.name!r})"


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(
        null=False,
        blank=True,
        verbose_name=_("Delivery Address"),
        help_text=_("Enter the delivery address"),
    )

    promocode = models.CharField(
        max_length=20,
        null=False,
        blank=True,
        verbose_name=_("Promo Code"),
        help_text=_("Enter promotional code if available"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Date and time when order was created"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Customer"),
        help_text=_("Customer who placed the order"),
    )

    products = models.ManyToManyField(
        Product,
        related_name="orders",
        verbose_name=_("Products"),
        help_text=_("Products included in the order"),
    )

    receipt = models.FileField(
        null=True,
        upload_to="orders/receipts/",
        verbose_name=_("Receipt"),
        help_text=_("Order receipt document"),
    )

    def __str__(self):
        return _("Order #{pk}").format(pk=self.pk)

    def get_orders_count(self, count):
        return ngettext("One order", "%(count) orders", count) % {"count": count}

    def get_products_in_order_count(self):
        count = self.products.count()
        return ngettext("One product in order", "%(count) products in order", count) % {
            "count": count
        }
