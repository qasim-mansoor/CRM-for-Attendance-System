# Generated by Django 5.0 on 2023-12-30 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_alter_customer_emergencynumber_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='customerName',
            new_name='customer_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='emergencyNumber',
            new_name='emergency_number',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='fatherName',
            new_name='father_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='phoneNumber',
            new_name='phone_number',
        ),
    ]
