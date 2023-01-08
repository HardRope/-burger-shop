from django.db import models
from django.utils import timezone

class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=200,
        unique=True,
    )

    lng = models.DecimalField(
        'Долгота',
        max_digits=22,
        decimal_places=16,
    )
    lat = models.DecimalField(
        'Широта',
        max_digits=22,
        decimal_places=16,
    )

    date = models.DateField(
        'Дата обновления',
        default=timezone.now,
        db_index=True,
    )
