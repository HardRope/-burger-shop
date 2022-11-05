import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        order_input = request.data

        order = Order.objects.create(
            name=order_input['firstname'],
            lastname=order_input['lastname'],
            phone=order_input['phonenumber'],
            address=order_input['address'],
        )

        for product in order_input['products']:
            OrderProduct.objects.create(
                product=Product.objects.get(id=product['product']),
                order=order,
                count=product['quantity']

            )

    except ValueError:
        return Response({
            'error': 'something bad',
        })
    return Response({})


{'products': [{'product': 6, 'quantity': 1}, {'product': 3, 'quantity': 1}, {'product': 1, 'quantity': 1}],
 'firstname': 'Вячеслав', 'lastname': 'Волков', 'phonenumber': '89313147092', 'address': 'Дачный Проспект, д. 36к8'}
