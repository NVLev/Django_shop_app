from django.core.management import BaseCommand
from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Update orders
    """

    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write("no order")
            return
        products = Product.objects.all()
        for product in products:
            order.products.add(product)  # менеджер связи many-to-many
        order.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Success! Added products {order.products.all()} to order {order}"
            )
        )
