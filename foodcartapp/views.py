from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField, IntegerField
from rest_framework.serializers import ModelSerializer, ValidationError
from django.core.validators import MinValueValidator

from .models import Product, Order, OrderProduct


class OrderProductSerializer(Serializer):
    quantity = IntegerField(validators=[MinValueValidator(0),])
    product = IntegerField()

    def validate_product(self, value):
        try:
            product = Product.objects.get(id=value)
        except ObjectDoesNotExist:
            raise ValidationError('Wrong product id')
        return product


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
        ]


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
@parser_classes([JSONParser])
def register_order(request):
    order_input = request.data

    # TODO починить передачу данных в сериалайзер
    serializer = OrderSerializer(data=order_input)
    serializer.is_valid(raise_exception=False)

    # order = Order.objects.create(
    #     firstname=serializer.validated_data['firstname'],
    #     lastname=serializer.validated_data['lastname'],
    #     phonenumber=serializer.validated_data['phonenumber'],
    #     address=serializer.validated_data['address'],
    # )

    # order_products_fields = serializer.validated_data['products']
    # order_products = [OrderProduct(
    #     order=order,
    #     quantity=fields['quantity'],
    #     product=fields['product']) for fields in order_products_fields]
    # OrderProduct.objects.bulk_create(order_products)

    order = Order.objects.create(
        firstname=order_input['firstname'],
        lastname=order_input['lastname'],
        phonenumber=order_input['phonenumber'],
        address=order_input['address'],
    )

    for product in order_input['products']:
        OrderProduct.objects.create(
            product=Product.objects.get(id=product['product']),
            order=order,
            quantity=product['quantity']
        )
    return Response({})

