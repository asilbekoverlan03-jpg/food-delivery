from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


# ─── Пользователь ─────────────────────────────────────────────────────────────
class UserProfile(AbstractUser):
    """Расширенный пользователь: адрес, телефон, аватар."""
    delivery_address = models.CharField('Адрес доставки', max_length=500, blank=True)
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    date_register = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


# ─── Ресторан ─────────────────────────────────────────────────────────────────
class Restaurant(models.Model):
    name = models.CharField('Название', max_length=200)
    logo = models.ImageField('Логотип', upload_to='restaurants/logos/', blank=True, null=True)
    address = models.CharField('Адрес', max_length=500)
    description = models.TextField('Описание', blank=True)
    delivery_time = models.PositiveIntegerField('Время доставки (мин)', default=30)
    min_order_price = models.DecimalField('Мин. сумма заказа', max_digits=8, decimal_places=2, default=0)
    is_open = models.BooleanField('Открыт', default=True)

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_avg_rating(self):
        """Средний рейтинг по отзывам; 0 если отзывов нет."""
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        total = sum(r.stars for r in reviews)
        return round(total / reviews.count(), 1)


# ─── Категория меню ───────────────────────────────────────────────────────────
class MenuCategory(models.Model):
    name = models.CharField('Название категории', max_length=100)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name='categories', verbose_name='Ресторан'
    )

    class Meta:
        verbose_name = 'Категория меню'
        verbose_name_plural = 'Категории меню'

    def __str__(self):
        return f'{self.restaurant.name} — {self.name}'


# ─── Позиция меню ─────────────────────────────────────────────────────────────
class MenuItem(models.Model):
    name = models.CharField('Название блюда', max_length=200)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    photo = models.ImageField('Фото', upload_to='menu/photos/', blank=True, null=True)
    weight = models.PositiveIntegerField('Вес (г)', default=0)
    is_available = models.BooleanField('Доступно', default=True)
    category = models.ForeignKey(
        MenuCategory, on_delete=models.CASCADE,
        related_name='items', verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Позиция меню'
        verbose_name_plural = 'Позиции меню'

    def __str__(self):
        return f'{self.name} ({self.category.restaurant.name})'


# ─── Корзина ──────────────────────────────────────────────────────────────────
class Cart(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE,
        related_name='cart', verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {self.user.username}'

    def get_total_price(self):
        return sum(ci.item.price * ci.quantity for ci in self.items.select_related('item').all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name='items', verbose_name='Корзина'
    )
    item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE,
        verbose_name='Блюдо'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ('cart', 'item')

    def __str__(self):
        return f'{self.item.name} × {self.quantity}'


# ─── Заказ ────────────────────────────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('preparing', 'Готовится'),
        ('on_way', 'В пути'),
        ('delivered', 'Доставлен'),
    ]

    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Пользователь'
    )
    items = models.ManyToManyField(MenuItem, through='OrderItem', verbose_name='Блюда')
    delivery_address = models.CharField('Адрес доставки', max_length=500)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_date']

    def __str__(self):
        return f'Заказ #{self.pk} ({self.user.username})'

    def get_total_price(self):
        return sum(oi.price * oi.quantity for oi in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='order_items', verbose_name='Заказ'
    )
    item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE,
        verbose_name='Блюдо'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена на момент заказа', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.item.name} × {self.quantity}'


# ─── Отзыв ────────────────────────────────────────────────────────────────────
class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Ресторан'
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Пользователь'
    )
    stars = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField('Комментарий', blank=True)
    created_date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('restaurant', 'user')
        ordering = ['-created_date']

    def __str__(self):
        return f'{self.user.username} → {self.restaurant.name} ({self.stars}★)'


# ─── Сигнал: создаём корзину при регистрации ──────────────────────────────────
@receiver(post_save, sender=UserProfile)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
