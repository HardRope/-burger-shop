import requests
from geopy import distance

from django import forms
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order
from locations.models import Location


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def get_restaurants(order, restaurants):
    order_products = [order_product.product for order_product in order.products.all()]
    for product in order_products:
        product_restaurants = {product_restaurant.restaurant
                               for product_restaurant in product.menu_items.all() if product_restaurant.availability}
        restaurants = restaurants.intersection(product_restaurants)
    return restaurants


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lng, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lng, lat


@transaction.atomic
def get_location(address, yandex_api_key):
    location, location_created = Location.objects.get_or_create(address=address)
    if location_created:
        coordinates = fetch_coordinates(yandex_api_key, address)
        if coordinates:
            location.lng = coordinates[0]
            location.lat = coordinates[1]
            location.save()
    return location


def get_distance(location, restaurant_location):
    order_coordinates = (location.lat, location.lng)
    restaurant_coordinates = (restaurant_location.lat, restaurant_location.lng)
    return distance.distance(order_coordinates, restaurant_coordinates).km


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.with_price().prefetch_related('order_products__product__menu_items__restaurant')

    order_items = []
    available_restaurants = set(Restaurant.objects.all())
    restaurant_locations = {restaurant.address: get_location(restaurant.address, settings.YANDEX_API_KEY)
                            for restaurant in available_restaurants}

    for order in orders:
        if order.status == 'CO':
            continue

        if order.restaurant:
            restaurant_text = f'Заказ готовится'
            restaurants = [order.restaurant]
        elif get_restaurants(order, available_restaurants):
            restaurant_text = f'Заказ может быть выполнен ресторанами:'
            restaurants = get_restaurants(order, available_restaurants)
        else:
            restaurant_text = 'Не можем определить ресторан'
            restaurants = None

        restaurants_distance = []
        try:
            location = get_location(order.address, settings.YANDEX_API_KEY)
            if restaurants:
                for restaurant in restaurants:
                    distance = get_distance(location, restaurant_locations[restaurant.address])
                    restaurants_distance.append({'restaurant':restaurant, 'distance': round(distance, 3)})
        except requests.RequestException:
            if restaurants:
                for restaurant in restaurants:
                    restaurants_distance.append({'restaurant': restaurant, 'distance': 0})

        order_item = {
            'id': order.id,
            'status': order.get_status_display(),
            'payment': order.get_payment_display(),
            'order_cost': order.order_cost,
            'name': f'{order.firstname} {order.lastname}',
            'phonenumber': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
            'restaurant_text': restaurant_text,
            'restaurants': restaurants_distance,
            'url': reverse('admin:foodcartapp_order_change', args=(order.id,)),
            'current_url': request.path,
        }
        order_items.append(order_item)

    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
    })
