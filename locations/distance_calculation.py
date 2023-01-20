from geopy import distance

def get_distance(location, restaurant_location):
    order_coordinates = location.lat, location.lng
    restaurant_coordinates = restaurant_location.lat, restaurant_location.lng
    return distance.distance(order_coordinates, restaurant_coordinates).km
