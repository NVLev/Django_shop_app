# Generated by Django 5.1.3 on 2025-01-14 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="pub_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
