from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSitemap(Sitemap):
    """
    Карта-сайта для товаров
    """

    changefreq = "monthly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at
