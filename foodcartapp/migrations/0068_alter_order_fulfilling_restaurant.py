# Generated by Django 3.2 on 2023-03-13 16:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0067_rename_payment_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='fulfilling_restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurant', to='foodcartapp.restaurant', verbose_name='исполняющий ресторан'),
        ),
    ]