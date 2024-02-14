# Generated by Django 5.0 on 2024-02-07 21:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0004_alter_customer_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="last_paid",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
