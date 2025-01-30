from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Avg, Count, Max, Min
from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("demo aggregate")
        result = Product.objects.aggregate(
            Avg("price"),
            Max("price"),
            Min("price"),
            Count("id"),
        )
        print(result)
        self.stdout.write("Done")
