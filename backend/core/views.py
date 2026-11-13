from django.db import transaction
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    UserProfile, Restaurant, MenuCategory, MenuItem,
    Cart, CartItem, Order, OrderItem, RestaurantReview,
)
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer,
    RestaurantListSerializer, RestaurantDetailSerializer,
    MenuCategorySerializer, MenuItemSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer,
    RestaurantReviewSerializer,
)
from .permissions import IsOwner, IsAdminOrReadOnly


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация нового пользователя."""
    queryset = UserProfile.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — просмотр и обновление профиля."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    # аватар — multipart, поэтому парсим partial update правильно
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


# ─── РЕСТОРАНЫ ────────────────────────────────────────────────────────────────

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/restaurants/           — список
    GET /api/restaurants/{id}/      — детали + меню
    GET /api/restaurants/{id}/reviews/  — отзывы
    POST /api/restaurants/{id}/reviews/ — добавить отзыв
    """
    queryset = Restaurant.objects.prefetch_related(
        'categories__items', 'reviews'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_open']
    search_fields = ['name', 'description']
    ordering_fields = ['delivery_time', 'min_order_price']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantListSerializer

    @action(detail=True, methods=['get', 'post'], url_path='reviews')
    def reviews(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            qs = restaurant.reviews.select_related('user').all()
            serializer = RestaurantReviewSerializer(qs, many=True)
            return Response(serializer.data)

        # POST — только авторизованные
        if not request.user.is_authenticated:
            return Response({'detail': 'Необходима авторизация.'}, status=401)

        # проверяем, нет ли уже отзыва
        if RestaurantReview.objects.filter(restaurant=restaurant, user=request.user).exists():
            return Response(
                {'detail': 'Вы уже оставили отзыв на этот ресторан.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RestaurantReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(restaurant=restaurant, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─── МЕНЮ ─────────────────────────────────────────────────────────────────────

class MenuCategoryViewSet(viewsets.ModelViewSet):
    """CRUD категорий — запись только для админа."""
    queryset = MenuCategory.objects.select_related('restaurant').prefetch_related('items').all()
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['restaurant']


class MenuItemViewSet(viewsets.ModelViewSet):
    """CRUD позиций меню — запись только для админа."""
    queryset = MenuItem.objects.select_related('category__restaurant').all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category__restaurant', 'category', 'is_available']
    search_fields = ['name', 'description']

    # удобный алиас: ?restaurant=<id>
    def get_queryset(self):
        qs = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            qs = qs.filter(category__restaurant_id=restaurant_id)
        return qs


# ─── КОРЗИНА ──────────────────────────────────────────────────────────────────

class CartView(generics.RetrieveAPIView):
    """GET /api/cart/ — корзина текущего пользователя."""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.prefetch_related('items__item').get_or_create(user=self.request.user)
        return cart


class CartItemView(APIView):
    """POST /api/cart/items/ — добавить блюдо в корзину."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            menu_item = MenuItem.objects.select_related('category__restaurant').get(pk=item_id)
        except MenuItem.DoesNotExist:
            return Response({'detail': 'Блюдо не найдено.'}, status=404)

        if not menu_item.is_available:
            return Response({'detail': 'Блюдо недоступно для заказа.'}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        # нельзя смешивать блюда из разных ресторанов
        existing_items = cart.items.select_related('item__category__restaurant').all()
        if existing_items.exists():
            first_restaurant = existing_items.first().item.category.restaurant
            if menu_item.category.restaurant != first_restaurant:
                return Response(
                    {'detail': (
                        f'В корзине уже есть блюда из "{first_restaurant.name}". '
                        'Очистите корзину, чтобы заказать из другого ресторана.'
                    )},
                    status=400
                )

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=menu_item)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=201)


class CartItemDetailView(APIView):
    """PATCH /api/cart/items/{id}/ и DELETE /api/cart/items/{id}/"""
    permission_classes = [IsAuthenticated]

    def _get_item(self, pk, user):
        try:
            return CartItem.objects.get(pk=pk, cart__user=user)
        except CartItem.DoesNotExist:
            return None

    def patch(self, request, pk):
        cart_item = self._get_item(pk, request.user)
        if not cart_item:
            return Response({'detail': 'Позиция не найдена.'}, status=404)

        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) < 1:
            return Response({'detail': 'Количество должно быть >= 1.'}, status=400)
        cart_item.quantity = int(quantity)
        cart_item.save()
        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, pk):
        cart_item = self._get_item(pk, request.user)
        if not cart_item:
            return Response({'detail': 'Позиция не найдена.'}, status=404)
        cart_item.delete()
        return Response(status=204)


class CartClearView(APIView):
    """DELETE /api/cart/clear/ — очистить корзину."""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(status=204)


# ─── ЗАКАЗЫ ───────────────────────────────────────────────────────────────────

class OrderViewSet(viewsets.ModelViewSet):
    """
    GET    /api/orders/         — мои заказы (admin видит все)
    POST   /api/orders/         — оформить заказ из корзины
    GET    /api/orders/{id}/    — детали заказа
    PATCH  /api/orders/{id}/status/ — смена статуса (только admin)
    DELETE /api/orders/{id}/    — отмена (только владелец, статус new)
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related(
            'order_items__item__category__restaurant'
        ).select_related('user')
        if user.is_staff:
            return qs.all()
        return qs.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # владелец или админ
        if instance.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Нет доступа.'}, status=403)
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Оформление заказа из корзины."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery_address = (
            serializer.validated_data.get('delivery_address')
            or request.user.delivery_address
        )
        if not delivery_address:
            return Response({'detail': 'Укажите адрес доставки.'}, status=400)

        cart = Cart.objects.prefetch_related('items__item__category__restaurant').get(user=request.user)

        if not cart.items.exists():
            return Response({'detail': 'Корзина пуста.'}, status=400)

        # Берём ресторан из первого блюда
        restaurant = cart.items.first().item.category.restaurant

        if not restaurant.is_open:
            return Response({'detail': f'Ресторан "{restaurant.name}" сейчас закрыт.'}, status=400)

        total = cart.get_total_price()
        if total < restaurant.min_order_price:
            return Response(
                {'detail': (
                    f'Минимальная сумма заказа для "{restaurant.name}" — '
                    f'{restaurant.min_order_price} сом. Сейчас у вас {total} сом.'
                )},
                status=400
            )

        order = Order.objects.create(user=request.user, delivery_address=delivery_address)
        for ci in cart.items.all():
            OrderItem.objects.create(
                order=order,
                item=ci.item,
                quantity=ci.quantity,
                price=ci.item.price,   # фиксируем цену на момент заказа
            )

        cart.items.all().delete()  # очищаем корзину

        return Response(OrderSerializer(order).data, status=201)

    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[IsAdminUser])
    def set_status(self, request, pk=None):
        """PATCH /api/orders/{id}/status/ — смена статуса (только admin)."""
        order = self.get_object()
        STATUS_FLOW = ['new', 'preparing', 'on_way', 'delivered']
        new_status = request.data.get('status')

        if new_status not in STATUS_FLOW:
            return Response({'detail': 'Недопустимый статус.'}, status=400)

        current_idx = STATUS_FLOW.index(order.status)
        new_idx = STATUS_FLOW.index(new_status)
        if new_idx != current_idx + 1:
            return Response(
                {'detail': f'Нельзя сменить статус с "{order.status}" на "{new_status}".'},
                status=400
            )

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

    def destroy(self, request, *args, **kwargs):
        """Отмена заказа — только владелец, статус new."""
        order = self.get_object()
        if order.user != request.user:
            return Response({'detail': 'Нет доступа.'}, status=403)
        if order.status != 'new':
            return Response(
                {'detail': 'Можно отменить только новый заказ.'},
                status=400
            )
        order.delete()
        return Response(status=204)
