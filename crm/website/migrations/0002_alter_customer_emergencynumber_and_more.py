# Generated by Django 5.0 on 2023-12-30 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='emergencyNumber',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phoneNumber',
            field=models.CharField(max_length=15),
        ),
    ]
