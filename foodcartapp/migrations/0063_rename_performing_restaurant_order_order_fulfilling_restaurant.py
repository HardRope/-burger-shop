# Generated by Django 3.2.15 on 2023-01-17 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0062_auto_20230117_1755'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='performing_restaurant',
            new_name='order_fulfilling_restaurant',
        ),
    ]
