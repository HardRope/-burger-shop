# Generated by Django 3.2.15 on 2023-01-17 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20230108_0823'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='date',
            new_name='updated_at',
        ),
    ]
