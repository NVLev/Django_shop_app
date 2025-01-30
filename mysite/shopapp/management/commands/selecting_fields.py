from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Start demo select fields
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")
        user_info = User.objects.values_list("pk", "username")
        # product_values = Product.objects.values("pk", "name")
        # for u_inf in user_info:
        print(list(user_info))
        print(user_info)
        self.stdout.write("Done")
