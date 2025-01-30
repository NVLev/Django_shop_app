import decimal
from csv import DictReader
from io import TextIOWrapper

from django.http import HttpRequest
from shopapp.models import Product


def save_csv_products(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [Product(**row, created_by=user) for row in reader]
    Product.objects.bulk_create(products)

    return products
