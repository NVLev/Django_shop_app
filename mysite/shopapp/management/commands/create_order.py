from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates orders
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        products: Sequence[Product] = Product.objects.all()
        order, created = Order.objects.get_or_create(
            delivery_address="Toreza, 5, Obninsk",
            promocode="Promo135",
            user=user,
        )
        for product in products:
            order.products.add(product)
        self.stdout.write(f"Created orderis {order}")
