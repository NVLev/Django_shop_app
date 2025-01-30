from itertools import product
from random import choices
from string import ascii_letters
from traceback import format_exception_only

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse
from shopapp.models import Order, Product


class ProductListViewTestCase(TestCase):
    fixtures = [
        "user-fixture.json",
        "group-fixture.json",
        "product-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(
            reverse("shopapp:products_list"), HTTP_USER_AGENT="Mozilla/5.0"
        )

        self.assertQuerySetEqual(
            # какие данные ожидаем получить
            qs=Product.objects.filter(archived=False).all(),
            # какие данные получили
            values=[p.pk for p in response.context["products"]],
            # как преобразовать данные, чтобы сравнить
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products_list.html")


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="test_user", password="password")
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        login_successful = self.client.login(**self.credentials)
        self.assertTrue(login_successful)

    def test_orders_view(self):
        response = self.client.get(
            reverse("shopapp:order_list"), HTTP_USER_AGENT="Mozilla/5.0"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(
            reverse("shopapp:order_list"), HTTP_USER_AGENT="Mozilla/5.0"
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailsViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="test_user", password="password")
        cls.user = User.objects.create_user(**cls.credentials)
        view_order_permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(view_order_permission)
        cls.order = Order.objects.create(
            delivery_address="".join(choices(ascii_letters, k=10)),
            promocode="TEST123",
            user=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        login_successful = self.client.login(**self.credentials)
        self.assertTrue(login_successful)

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_detail", kwargs={"pk": self.order.pk}),
            HTTP_USER_AGENT="Mozilla/5.0",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "user-fixture.json",
        "group-fixture.json",
        "order-fixture.json",
        "product-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="test_user", password="password")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        login_successful = self.client.login(**self.credentials)
        self.assertTrue(login_successful)

    def test_get_orders_view(self):
        response = self.client.get(
            reverse("shopapp:order_export"), HTTP_USER_AGENT="Mozilla/5.0"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        orders_data = response.json()
        self.assertIn("orders", orders_data)
        for order in orders_data["orders"]:
            self.assertIn("pk", order)
            self.assertIn("delivery_address", order)
            self.assertIn("promocode", order)
            self.assertIn("user", order)
            self.assertIn("products", order)

            for product in order["products"]:
                self.assertIn("name", product)
                self.assertIn("price", product)
