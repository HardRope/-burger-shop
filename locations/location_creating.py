from django.db import transaction

from .models import Location
from .yandex_geocode_api import fetch_coordinates


@transaction.atomic
def get_location(address, yandex_api_key):
    location, location_created = Location.objects.get_or_create(address=address)
    if location_created:
        coordinates = fetch_coordinates(yandex_api_key, address)
        if coordinates:
            lng, lat = coordinates
            location.lng = lng
            location.lat = lat
            location.save()
    return location
