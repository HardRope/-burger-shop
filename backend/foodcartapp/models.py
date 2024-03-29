from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_price(self):
        return self.annotate(order_cost=Sum(F('order_products__fixed_price') * F('order_products__quantity')))


class Order(models.Model):
    RAW = 'RW'
    PROCESSED = 'PR'
    DELIVERY = 'DE'
    COMPLETE = 'CO'
    STATUS_CHOICES = [
        (RAW, 'Необработанный'),
        (PROCESSED, 'В ресторане'),
        (DELIVERY, 'В доставке'),
        (COMPLETE, 'Завершен')
    ]

    CASH = 'CS'
    E_PAY = 'EP'
    PAYMENT_CHOICES = [
        (CASH, 'Наличные'),
        (E_PAY, 'Электронная оплата')
    ]

    status = models.CharField(
        'статус заказа',
        max_length=2,
        choices=STATUS_CHOICES,
        default=RAW,
        db_index=True,
    )

    payment_method = models.CharField(
        'способ оплаты',
        max_length=2,
        choices=PAYMENT_CHOICES,
        null=True,
        db_index=True,
    )

    firstname = models.CharField('Имя', max_length=20)
    lastname = models.CharField('Фамилия', max_length=20)
    phonenumber = PhoneNumberField(
        'Телефон',
        db_index=True,
    )
    address = models.CharField('Адрес', max_length=100)
    comment = models.TextField('Комментарий', blank=True)

    fulfilling_restaurant = models.ForeignKey(
        Restaurant,
        related_name='restaurant',
        verbose_name='исполняющий ресторан',
        on_delete=models.CASCADE,
        null=True
    )

    registrated_at = models.DateTimeField(
        'Зарегистрирован', default=timezone.now, db_index=True,)
    called_at = models.DateTimeField(
        'Созвон', blank=True, null=True, db_index=True,)
    delivered_at = models.DateTimeField(
        'Доставлен', blank=True, null=True, db_index=True,)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderProduct(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        related_name='order_products',
        on_delete=models.DO_NOTHING,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='order_products',
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1), ]
    )

    fixed_price = models.DecimalField(
        'фиксированная стоимость',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), ]
    )

    class Meta:
        verbose_name = 'позиция'
        verbose_name_plural = 'позиции'

    def __str__(self):
        return f'{self.quantity} {self.product.name}'
