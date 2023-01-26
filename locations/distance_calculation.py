from geopy import distance

def get_distance(first_location, second_location):
    if not all([first_location, second_location]):
        return 0
    first_coordinates = first_location.lat, first_location.lng
    second_coordinates = second_location.lat, second_location.lng
    return distance.distance(first_coordinates, second_coordinates).km
