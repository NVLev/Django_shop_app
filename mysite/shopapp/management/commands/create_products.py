from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write("Create products")
        product_names = [
            "T-shirt",
            "Cup",
            "Calendar",
        ]
        for product_name in product_names:
            product, created = Product.objects.get_or_create(name=product_name)
            self.stdout.write(f"Created product is {product.name}")
        self.stdout.write(self.style.SUCCESS("Product created"))
