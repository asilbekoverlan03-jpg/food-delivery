from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserProfile, Restaurant, MenuCategory, MenuItem,
    Cart, CartItem, Order, OrderItem, RestaurantReview,
)


# ─── AUTH / ПОЛЬЗОВАТЕЛЬ ──────────────────────────────────────────────────────

class UserRegisterSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Подтверждение пароля')

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'password', 'password2',
                  'phone_number', 'delivery_address')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Пароли не совпадают.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = UserProfile(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Просмотр и обновление профиля."""
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'phone_number',
                  'delivery_address', 'avatar', 'date_register')
        read_only_fields = ('id', 'username', 'date_register')


# ─── МЕНЮ ─────────────────────────────────────────────────────────────────────

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'price', 'description', 'photo',
                  'weight', 'is_available', 'category')


class MenuCategorySerializer(serializers.ModelSerializer):
    """Категория со вложенными блюдами (для страницы ресторана)."""
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'restaurant', 'items')


# ─── РЕСТОРАН ─────────────────────────────────────────────────────────────────

class RestaurantListSerializer(serializers.ModelSerializer):
    """Краткая карточка для списка ресторанов."""
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'logo', 'address', 'description',
                  'delivery_time', 'min_order_price', 'is_open',
                  'avg_rating', 'reviews_count')

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Детальная страница ресторана с меню по категориям."""
    categories = MenuCategorySerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'logo', 'address', 'description',
                  'delivery_time', 'min_order_price', 'is_open',
                  'avg_rating', 'reviews_count', 'categories')

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_reviews_count(self, obj):
        return obj.reviews.count()


# ─── ОТЗЫВ ────────────────────────────────────────────────────────────────────

class RestaurantReviewSerializer(serializers.ModelSerializer):
    # user подставляется из request, не передаётся клиентом
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = RestaurantReview
        fields = ('id', 'user', 'username', 'restaurant',
                  'stars', 'comment', 'created_date')
        read_only_fields = ('id', 'user', 'username', 'restaurant', 'created_date')

    def validate_stars(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Оценка должна быть от 1 до 5.')
        return value


# ─── КОРЗИНА ──────────────────────────────────────────────────────────────────

class CartItemSerializer(serializers.ModelSerializer):
    # вложенный объект блюда для чтения
    item = MenuItemSerializer(read_only=True)
    # id блюда для записи
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'item', 'item_id', 'quantity')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price')

    def get_total_price(self, obj):
        return obj.get_total_price()


# ─── ЗАКАЗ ────────────────────────────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    """Чтение заказа с составом и суммой."""
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_items', 'delivery_address',
                  'status', 'created_date', 'total_price')
        read_only_fields = ('id', 'user', 'status', 'created_date')

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderCreateSerializer(serializers.Serializer):
    """Создание заказа из корзины."""
    delivery_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
