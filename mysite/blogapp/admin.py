from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticAdmin(admin.ModelAdmin):
    list_display = "id", "title", "content", "pub_date"
