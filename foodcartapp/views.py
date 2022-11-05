from phonenumber_field.phonenumber import PhoneNumber
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
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
        if not isinstance(order_input['firstname'], str):
            raise ValueError('firstname')
        if not isinstance(order_input['lastname'], str):
            raise ValueError('lastname')
        if not isinstance(order_input['address'], str):
            raise ValueError('address')
        if not order_input['phonenumber']:
            raise KeyError('phonenumber')
        if isinstance(order_input['products'], list) and not order_input['products']:
            raise KeyError('products')

        phone = PhoneNumber.from_string(order_input['phonenumber'], region='RU')
        if not phone.is_valid():
            raise ValueError('phonenumber')

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
    except IntegrityError as integrity:
        return Response({
            'error': f'{integrity} error'
        })
    except ObjectDoesNotExist as error:
        return Response({
            'error': f'{error}'
        })
    except TypeError:
        return Response({
            'error': 'products are not list'
        })
    except KeyError as key:
        return Response({
            'error': f'missing {key} value'
        })
    except ValueError as value:
        return Response({
            'error': f'wrong {value} value',
        })
    return Response({})
