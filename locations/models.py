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
        null=True
    )
    lat = models.DecimalField(
        'Широта',
        max_digits=22,
        decimal_places=16,
        null=True
    )

    updated_at = models.DateField(
        'Дата обновления',
        default=timezone.now,
        db_index=True,
    )

    def __str__(self):
        return self.address
