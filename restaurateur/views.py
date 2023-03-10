import requests

from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order
from locations.models import Location
from locations.location_creating import get_location
from locations.distance_calculation import get_distance

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


def get_possible_restaurants(order, restaurants):
    order_products = [order_product.product for order_product in order.order_products.all()]
    for product in order_products:
        product_restaurants = {product_restaurant.restaurant
                               for product_restaurant in product.menu_items.all() if product_restaurant.availability}
        restaurants = restaurants.intersection(product_restaurants)
    return restaurants


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
    orders = Order.objects.with_price().exclude(status='CO').order_by('id').\
        prefetch_related('order_products__product__menu_items__restaurant')

    available_restaurants = set(Restaurant.objects.all())

    restaurant_addresses = [restaurant.address for restaurant in available_restaurants]
    restaurant_locations = Location.objects.in_bulk(restaurant_addresses, field_name='address')
    order_addresses = [order.address for order in orders]
    order_locations = Location.objects.in_bulk(order_addresses, field_name='address')

    new_address_locations = []
    for address in restaurant_addresses:
        if address not in restaurant_locations.keys():
            try:
                address_location = get_location(address, settings.YANDEX_API_KEY)
                new_address_locations.append(address_location)
                restaurant_locations[address] = address_location
            except requests.RequestException:
                restaurant_locations[address] = None

    for address in order_addresses:
        if address not in order_locations.keys():
            try:
                address_location = get_location(address, settings.YANDEX_API_KEY)
                new_address_locations.append(address_location)
                order_locations[address] = address_location
            except requests.RequestException:
                order_locations[address] = None

    Location.objects.bulk_create(filter(None, new_address_locations), ignore_conflicts=True)

    order_collections = []
    for order in orders:
        if order.fulfilling_restaurant:
            restaurant_text = f'Заказ готовится'
            restaurants = [order.fulfilling_restaurant]
        elif get_possible_restaurants(order, available_restaurants):
            restaurant_text = f'Заказ может быть выполнен ресторанами:'
            restaurants = get_possible_restaurants(order, available_restaurants)
        else:
            restaurant_text = 'Не можем определить ресторан'
            restaurants = None

        restaurants_distance = []
        location = order_locations[order.address]

        if location and restaurants:
            for restaurant in restaurants:
                restaurant_location = restaurant_locations.get(restaurant.address)
                restaurant_address = restaurant.address

                distance = 0
                if restaurant_location:
                    distance = get_distance(location, restaurant_location)

                restaurants_distance.append(
                    {
                        'restaurant_address': restaurant_address,
                        'distance': round(distance, 3)
                    })

        order_collection = {
            'id': order.id,
            'status': order.get_status_display(),
            'payment': order.get_payment_method_display(),
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
        order_collections.append(order_collection)

    return render(request, template_name='order_items.html', context={
        'order_collections': order_collections,
    })
