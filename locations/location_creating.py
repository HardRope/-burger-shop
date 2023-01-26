from .models import Location
from .yandex_geocode_api import fetch_coordinates


def get_location(address, yandex_api_key):
    coordinates = fetch_coordinates(yandex_api_key, address)
    if coordinates:
        lng, lat = coordinates
        location = Location(
            address=address,
            lng=lng,
            lat=lat,
        )
        return location
