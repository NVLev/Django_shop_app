# Generated by Django 5.1.3 on 2024-12-15 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0008_product_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="receipt",
            field=models.FileField(null=True, upload_to="orders/receipts/"),
        ),
    ]
