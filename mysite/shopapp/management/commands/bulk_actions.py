from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("bulk_actions")
        result = Product.objects.filter(
            name__contains="sh",
        ).update(discount=10)
        self.stdout.write("Done")
