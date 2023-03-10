# Generated by Django 3.2.15 on 2023-01-08 02:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, unique=True, verbose_name='Адрес')),
                ('lng', models.DecimalField(decimal_places=16, max_digits=22, verbose_name='Долгота')),
                ('lat', models.DecimalField(decimal_places=16, max_digits=22, verbose_name='Широта')),
                ('date', models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата обновления')),
            ],
        ),
    ]
